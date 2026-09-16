"""Register and execute a harmless custom tool."""

from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_company_core import AgentDecision, DecisionAction, MissionCreate, MissionEngine
from agent_company_core.models import ModelRequest, ModelResponse
from agent_company_core.persistence import SQLiteStore
from agent_company_core.tools import ToolRegistry, ToolSpec


class ToolDecisionModel:
    name = "tool-example"

    async def complete(self, request: ModelRequest) -> ModelResponse:
        decision = AgentDecision(
            action=DecisionAction.USE_TOOL,
            rationale="use the explicitly registered formatter",
            tool_name="format-note",
            tool_arguments={"text": "hello"},
        )
        return ModelResponse(
            text=decision.model_dump_json(),
            model="tool-example",
            provider=self.name,
            structured=decision,
        )


async def main() -> None:
    with TemporaryDirectory(prefix="agent-company-tool-") as temporary:
        tools = ToolRegistry()
        tools.register(
            ToolSpec(
                "format-note",
                "Format a local note",
                frozenset({"text"}),
                lambda arguments: {"formatted": str(arguments["text"]).upper()},
            )
        )
        engine = MissionEngine(
            store=SQLiteStore(Path(temporary) / "state.sqlite3"),
            providers={"fast": ToolDecisionModel()},
            tools=tools,
        )
        mission = engine.create_mission(
            MissionCreate(title="Format note", objective="Format a harmless note")
        )
        result = await engine.run_mission(mission.id)
        print(result.status.value, result.summary)


if __name__ == "__main__":
    asyncio.run(main())
