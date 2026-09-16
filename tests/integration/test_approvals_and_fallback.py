from pathlib import Path
from uuid import UUID

import pytest

from agent_company_core import (
    AgentDecision,
    DecisionAction,
    MissionCreate,
    RiskLevel,
)
from agent_company_core.models import FakeModel, ModelRequest, ModelResponse
from agent_company_core.orchestration import MissionEngine
from agent_company_core.persistence import SQLiteStore
from agent_company_core.tools import ToolRegistry, ToolSpec


class DecisionProvider:
    name = "test-provider"

    def __init__(self, decision: AgentDecision) -> None:
        self.decision = decision

    async def complete(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            text="", model="test-model", provider=self.name, structured=self.decision
        )


class FailingProvider:
    name = "failing-provider"

    async def complete(self, request: ModelRequest) -> ModelResponse:
        raise RuntimeError("temporary provider failure")


@pytest.mark.asyncio
async def test_approval_is_exact_and_effect_runs_only_after_resolution(tmp_path: Path) -> None:
    tools = ToolRegistry()
    tools.register(
        ToolSpec(
            "deploy",
            "test effect",
            frozenset({"release"}),
            lambda args: {"target": args["target"]},
            risk=RiskLevel.HIGH,
        )
    )
    decision = AgentDecision(
        action=DecisionAction.USE_TOOL,
        rationale="the declared policy requires a human",
        tool_name="deploy",
        tool_arguments={"target": "staging"},
    )
    engine = MissionEngine(
        store=SQLiteStore(tmp_path / "state.sqlite3"),
        providers={"fast": DecisionProvider(decision)},
        tools=tools,
    )
    mission = engine.create_mission(
        MissionCreate(title="Approval", objective="Apply a controlled change")
    )
    waiting = await engine.run_mission(mission.id)
    assert waiting.status.value == "waiting_approval"
    row = engine.store.list_approvals(mission.id)[0]
    from agent_company_core.permissions import ApprovalResolution

    engine.resolve_approval(
        UUID(row["id"]),
        ApprovalResolution(approved=True, resolved_by="operator", request_hash=row["request_hash"]),
    )
    result = await engine.execute_approved(UUID(row["id"]))
    assert result.output == {"target": "staging"}


@pytest.mark.asyncio
async def test_provider_fallback_is_explicit_and_audited(tmp_path: Path) -> None:
    fallback = FakeModel("fallback")
    engine = MissionEngine(
        store=SQLiteStore(tmp_path / "state.sqlite3"),
        providers={"fast": FailingProvider(), "reasoning": fallback},
    )
    mission = engine.create_mission(MissionCreate(title="Fallback", objective="Answer safely"))
    result = await engine.run_mission(mission.id)
    assert result.status.value == "completed"
    assert len(fallback.requests) == 1
    audit = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "model.failed" in audit
