"""A small durable mission engine composed from explicit interfaces."""

from __future__ import annotations

import inspect
import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from agent_company_core.agents import AgentRegistry, demo_registry
from agent_company_core.contracts import (
    TERMINAL_STATUSES,
    AgentDecision,
    DecisionAction,
    Mission,
    MissionCreate,
    MissionResult,
    MissionStatus,
    RiskLevel,
)
from agent_company_core.memory import MemoryItem, MemoryStore, SQLiteMemoryStore
from agent_company_core.models import (
    FakeModel,
    ModelProvider,
    ModelRequest,
    ModelResponse,
    RoutingAssessment,
    select_model_route,
)
from agent_company_core.observability import AuditLogger
from agent_company_core.permissions import (
    ApprovalRequest,
    ApprovalResolution,
    Policy,
    is_exact_match,
)
from agent_company_core.persistence import SQLiteStore
from agent_company_core.runtime import StopControl, StopRequested
from agent_company_core.tools import ToolRegistry, ToolResult


class MissionEngine:
    """Coordinate decisions and effects while keeping state in durable storage."""

    def __init__(
        self,
        *,
        store: SQLiteStore,
        providers: dict[str, ModelProvider] | None = None,
        agents: AgentRegistry | None = None,
        tools: ToolRegistry | None = None,
        policy: Policy | None = None,
        stop: StopControl | None = None,
        audit: AuditLogger | None = None,
        memory: MemoryStore | None = None,
    ) -> None:
        self.store = store
        fallback_model = FakeModel()
        self.providers = providers or {
            "fast": fallback_model,
            "reasoning": fallback_model,
            "vision": fallback_model,
        }
        self.agents = agents or demo_registry()
        self.tools = tools or ToolRegistry()
        self.policy = policy or Policy()
        self.stop = stop or StopControl(Path(store.path).with_name("stop.json"))
        self.audit = audit or AuditLogger(Path(store.path).with_name("audit.jsonl"))
        self.memory = memory or SQLiteMemoryStore(store.path)

    def create_mission(self, value: MissionCreate) -> Mission:
        mission = self.store.create_mission(value)
        self.audit.record(
            "mission.created", mission_id=str(mission.id), payload={"title": mission.title}
        )
        return mission

    def list_missions(self) -> list[Mission]:
        return self.store.list_missions()

    def get_mission(self, mission_id: UUID) -> Mission:
        return self.store.get_mission(mission_id)

    def choose_tool(self, capabilities: set[str]) -> str:
        tool = self.tools.choose(capabilities=capabilities)
        self.audit.record(
            "tool.selected", payload={"tool": tool.name, "capabilities": sorted(capabilities)}
        )
        return tool.name

    async def run_mission(
        self,
        mission_id: UUID,
        *,
        assessment: RoutingAssessment | None = None,
        capabilities: set[str] | None = None,
    ) -> MissionResult:
        mission = self.store.get_mission(mission_id)
        if mission.status in TERMINAL_STATUSES:
            return MissionResult(
                mission_id=mission.id,
                status=mission.status,
                summary="mission is already terminal",
                selected_agent=(mission.assigned_agents[0] if mission.assigned_agents else None),
                checkpoint=mission.checkpoint,
            )
        selected_agent = self.agents.select(capabilities=capabilities or set())
        assessment = assessment or RoutingAssessment(
            complexity=0.3, ambiguity=0.1, risk=0.1, continuity=0.2
        )
        route = select_model_route(
            assessment,
            fallbacks={"fast": ("reasoning",), "reasoning": ("fast",), "vision": ("reasoning",)},
        )
        self.store.set_status(mission.id, MissionStatus.QUEUED, payload={"route": route.primary})
        try:
            self.stop.assert_running()
            self.store.set_status(
                mission.id, MissionStatus.RUNNING, payload={"agent": selected_agent.id}
            )
            self.audit.record(
                "mission.started",
                mission_id=str(mission.id),
                payload={"agent": selected_agent.id, "route": route.candidates},
            )
            request = ModelRequest(
                prompt=mission.objective,
                system="Return a typed agent decision. Do not perform effects.",
                response_schema=AgentDecision,
                metadata={"mission_id": str(mission.id), "agent_id": selected_agent.id},
            )
            response = await self._complete(route.candidates, request, mission_id=mission.id)
            decision = (
                response.structured
                if isinstance(response.structured, AgentDecision)
                else AgentDecision(
                    action=DecisionAction.RESPOND,
                    rationale="provider returned text",
                    response=response.text,
                )
            )
            self.audit.record(
                "decision.recorded",
                mission_id=str(mission.id),
                payload=decision.model_dump(mode="json"),
            )
            return await self._apply_decision(mission.id, decision, selected_agent.id)
        except StopRequested as exc:
            self.store.set_status(mission.id, MissionStatus.STOPPED, payload={"reason": str(exc)})
            self.audit.record(
                "mission.stopped", mission_id=str(mission.id), payload={"reason": str(exc)}
            )
            return MissionResult(
                mission_id=mission.id,
                status=MissionStatus.STOPPED,
                summary=str(exc),
                selected_agent=selected_agent.id,
                checkpoint=mission.checkpoint,
            )
        except Exception as exc:
            self.store.set_status(
                mission.id, MissionStatus.FAILED, payload={"error_type": type(exc).__name__}
            )
            self.audit.record(
                "mission.failed",
                mission_id=str(mission.id),
                payload={"error_type": type(exc).__name__, "error": str(exc)},
            )
            return MissionResult(
                mission_id=mission.id,
                status=MissionStatus.FAILED,
                summary=f"mission failed: {type(exc).__name__}",
                selected_agent=selected_agent.id,
                checkpoint=mission.checkpoint,
            )

    async def _complete(
        self, candidates: tuple[str, ...], request: ModelRequest, *, mission_id: UUID
    ) -> ModelResponse:
        errors: list[str] = []
        for alias in candidates:
            provider = self.providers.get(alias)
            if provider is None:
                errors.append(f"{alias}: unavailable")
                continue
            try:
                result = await provider.complete(request)
                self.audit.record(
                    "model.completed",
                    mission_id=str(mission_id),
                    payload={
                        "provider": result.provider,
                        "model": result.model,
                        "route_alias": alias,
                    },
                )
                return result
            except Exception as exc:
                errors.append(f"{alias}: {type(exc).__name__}")
                self.audit.record(
                    "model.failed",
                    mission_id=str(mission_id),
                    payload={"route_alias": alias, "error_type": type(exc).__name__},
                )
                self.stop.assert_running()
        raise RuntimeError("all model routes failed: " + ", ".join(errors))

    async def _apply_decision(
        self, mission_id: UUID, decision: AgentDecision, agent_id: str
    ) -> MissionResult:
        self.stop.assert_running()
        if decision.action is DecisionAction.RESPOND:
            mission = self.store.set_status(
                mission_id, MissionStatus.COMPLETED, payload={"agent": agent_id}
            )
            summary = decision.response or decision.rationale
            self.memory.remember(
                MemoryItem(
                    content=summary,
                    scope=f"mission:{mission_id}",
                    key="latest_result",
                    metadata={"mission_id": str(mission_id)},
                )
            )
            return MissionResult(
                mission_id=mission_id,
                status=mission.status,
                summary=summary,
                selected_agent=agent_id,
                checkpoint=mission.checkpoint,
            )
        if decision.action is DecisionAction.DELEGATE:
            selected = decision.agent_ids or [
                agent.id for agent in self.agents.select_many(capabilities={"planning"}, limit=3)
            ]
            mission = self.store.assign_agents(mission_id, selected)
            mission = self.store.set_status(
                mission_id, MissionStatus.COMPLETED, payload={"delegated_to": selected}
            )
            return MissionResult(
                mission_id=mission_id,
                status=mission.status,
                summary="delegated to declared agents",
                selected_agent=selected[0] if selected else None,
                checkpoint=mission.checkpoint,
            )
        if decision.action is DecisionAction.CREATE_MISSION:
            if not decision.mission:
                raise ValueError("create_mission decision must include a mission payload")
            child = self.create_mission(MissionCreate.model_validate(decision.mission))
            mission = self.store.set_status(
                mission_id, MissionStatus.COMPLETED, payload={"child_mission_id": str(child.id)}
            )
            return MissionResult(
                mission_id=mission.id,
                status=mission.status,
                summary=f"created child mission {child.id}",
                selected_agent=agent_id,
                checkpoint=mission.checkpoint,
            )
        if decision.action is DecisionAction.USE_TOOL:
            name = decision.tool_name or self.choose_tool(set(decision.tool_capabilities))
            tool = self.tools.get(name)
            from agent_company_core.permissions import ActionRequest

            policy_decision = self.policy.evaluate(
                ActionRequest(
                    action=tool.name,
                    target=tool.name,
                    arguments=decision.tool_arguments,
                    requested_by=agent_id,
                    risk=tool.risk,
                    mission_id=str(mission_id),
                )
            )
            if not policy_decision.allowed:
                raise PermissionError(policy_decision.reason)
            if policy_decision.requires_approval:
                approval = ApprovalRequest.create(
                    action=tool.name,
                    target=tool.name,
                    arguments=decision.tool_arguments,
                    risk=tool.risk,
                    requested_by=agent_id,
                    mission_id=mission_id,
                )
                self.store.save_approval(approval)
                mission = self.store.set_status(
                    mission_id,
                    MissionStatus.WAITING_APPROVAL,
                    payload={
                        "approval_id": str(approval.id),
                        "request_hash": approval.request_hash,
                    },
                )
                return MissionResult(
                    mission_id=mission.id,
                    status=mission.status,
                    summary=f"approval required for {tool.name}",
                    selected_agent=agent_id,
                    selected_tool=tool.name,
                    checkpoint=mission.checkpoint,
                )
            result = await self.tools.execute(
                name,
                decision.tool_arguments,
                policy=self.policy,
                stop=self.stop,
                requested_by=agent_id,
                mission_id=str(mission_id),
            )
            mission = self.store.set_status(
                mission_id,
                MissionStatus.COMPLETED,
                payload={"tool": result.name, "output": result.output},
            )
            return MissionResult(
                mission_id=mission.id,
                status=mission.status,
                summary=json_summary(result),
                selected_agent=agent_id,
                selected_tool=result.name,
                checkpoint=mission.checkpoint,
            )
        if decision.action is DecisionAction.REQUEST_APPROVAL:
            approval = ApprovalRequest.create(
                action=decision.tool_name or "declared_effect",
                target=decision.tool_name or "declared_effect",
                arguments=decision.tool_arguments,
                risk=decision.risk,
                requested_by=agent_id,
                mission_id=mission_id,
            )
            self.store.save_approval(approval)
            mission = self.store.set_status(
                mission_id,
                MissionStatus.WAITING_APPROVAL,
                payload={"approval_id": str(approval.id), "request_hash": approval.request_hash},
            )
            return MissionResult(
                mission_id=mission.id,
                status=mission.status,
                summary="approval required",
                selected_agent=agent_id,
                checkpoint=mission.checkpoint,
            )
        mission = self.store.set_status(
            mission_id, MissionStatus.BLOCKED, payload={"rationale": decision.rationale}
        )
        return MissionResult(
            mission_id=mission.id,
            status=mission.status,
            summary=decision.rationale,
            selected_agent=agent_id,
            checkpoint=mission.checkpoint,
        )

    def resolve_approval(self, approval_id: UUID, resolution: ApprovalResolution) -> None:
        row = self.store.get_approval(approval_id)
        request = ApprovalRequest(
            id=approval_id,
            action=row["action"],
            target=row["target"],
            arguments=json.loads(row["arguments"]),
            risk=RiskLevel(row["risk"]),
            requested_by=row["requested_by"],
            mission_id=UUID(row["mission_id"]) if row["mission_id"] else None,
            request_hash=row["request_hash"],
            expires_at=datetime.fromisoformat(row["expires_at"]),
        )
        if not is_exact_match(request, resolution):
            raise PermissionError(
                "approval does not exactly match the requested effect or has expired"
            )
        self.store.resolve_approval(
            approval_id,
            approved=resolution.approved,
            resolved_by=resolution.resolved_by,
            request_hash=resolution.request_hash,
            arguments=resolution.modified_arguments,
        )
        if request.mission_id:
            self.store.set_status(
                request.mission_id,
                MissionStatus.QUEUED if resolution.approved else MissionStatus.CANCELLED,
                payload={"approval_id": str(approval_id), "approved": resolution.approved},
            )
        self.audit.record(
            "approval.resolved",
            mission_id=str(request.mission_id) if request.mission_id else None,
            payload={"approval_id": str(approval_id), "approved": resolution.approved},
        )

    async def execute_approved(self, approval_id: UUID) -> ToolResult:
        """Execute exactly one previously approved registered tool effect."""

        row = self.store.get_approval(approval_id)
        if row["status"] != "approved" or row["resolved_hash"] != row["request_hash"]:
            raise PermissionError("approval is not resolved for execution")
        self.stop.assert_running()
        tool = self.tools.get(row["action"])
        arguments = json.loads(row["arguments"])
        value = tool.handler(arguments)
        output = await value if inspect.isawaitable(value) else value
        mission_id = UUID(row["mission_id"]) if row["mission_id"] else None
        if mission_id:
            self.store.set_status(
                mission_id,
                MissionStatus.COMPLETED,
                payload={"approval_id": str(approval_id), "tool": tool.name, "output": output},
            )
        self.audit.record(
            "approved_effect.executed",
            mission_id=str(mission_id) if mission_id else None,
            payload={"approval_id": str(approval_id), "tool": tool.name},
        )
        return ToolResult(name=tool.name, output=output)

    def checkpoint(self, mission_id: UUID, value: str) -> Mission:
        return self.store.checkpoint(mission_id, value)

    def request_stop(self, reason: str = "requested") -> None:
        self.stop.request(reason)
        self.audit.record("runtime.stop_requested", payload={"reason": reason})

    def clear_stop(self) -> None:
        self.stop.clear()
        self.audit.record("runtime.stop_cleared")

    def remember(
        self,
        content: str,
        *,
        scope: str = "default",
        key: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> MemoryItem:
        item = self.memory.remember(
            MemoryItem(content=content, scope=scope, key=key, metadata=metadata or {})
        )
        self.audit.record("memory.persisted", payload={"memory_id": str(item.id), "scope": scope})
        return item

    def search_memory(
        self, query: str, *, scope: str | None = None, limit: int = 10
    ) -> list[MemoryItem]:
        return self.memory.search(query, scope=scope, limit=limit)


def json_summary(result: ToolResult) -> str:
    import json

    return json.dumps(result.output, sort_keys=True, ensure_ascii=False)
