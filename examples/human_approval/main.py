"""Pause a high-risk tool until an exact human approval is resolved."""

from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from agent_company_core import (
    AgentDecision,
    DecisionAction,
    MissionCreate,
    MissionEngine,
    RiskLevel,
)
from agent_company_core.models import ModelRequest, ModelResponse
from agent_company_core.permissions import ApprovalResolution
from agent_company_core.persistence import SQLiteStore
from agent_company_core.tools import ToolRegistry, ToolSpec


class ApprovalDecisionModel:
    name = "approval-example"

    async def complete(self, request: ModelRequest) -> ModelResponse:
        decision = AgentDecision(
            action=DecisionAction.USE_TOOL,
            rationale="the example asks for an explicitly approved effect",
            tool_name="stage-change",
            tool_arguments={"target": "staging"},
            risk=RiskLevel.HIGH,
        )
        return ModelResponse(
            text=decision.model_dump_json(),
            model="approval-example",
            provider=self.name,
            structured=decision,
        )


async def main() -> None:
    with TemporaryDirectory(prefix="agent-company-approval-") as temporary:
        root = Path(temporary)
        tools = ToolRegistry()
        tools.register(
            ToolSpec(
                "stage-change",
                "Record a harmless staging action",
                frozenset({"release"}),
                lambda arguments: {"target": arguments["target"], "applied": True},
                risk=RiskLevel.HIGH,
            )
        )
        model = ApprovalDecisionModel()
        engine = MissionEngine(
            store=SQLiteStore(root / "state.sqlite3"),
            providers={"fast": model},
            tools=tools,
        )
        mission = engine.create_mission(
            MissionCreate(title="Controlled change", objective="Prepare a staging change")
        )
        waiting = await engine.run_mission(mission.id)
        row = engine.store.list_approvals(mission.id)[0]
        print("before approval:", waiting.status.value)
        engine.resolve_approval(
            UUID(row["id"]),
            ApprovalResolution(
                approved=True,
                resolved_by="operator",
                request_hash=row["request_hash"],
            ),
        )
        result = await engine.execute_approved(UUID(row["id"]))
        print("after approval:", result.output)


if __name__ == "__main__":
    asyncio.run(main())
