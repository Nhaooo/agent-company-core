"""Implement the neutral provider protocol without an SDK."""

from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_company_core import AgentDecision, DecisionAction, MissionCreate, MissionEngine
from agent_company_core.models import ModelRequest, ModelResponse
from agent_company_core.persistence import SQLiteStore


class LocalProvider:
    name = "local-example"

    async def complete(self, request: ModelRequest) -> ModelResponse:
        decision = AgentDecision(
            action=DecisionAction.RESPOND,
            rationale="a local provider made a typed decision",
            response="custom provider completed",
        )
        return ModelResponse(
            text=decision.response or "",
            model="local-example",
            provider=self.name,
            structured=decision,
        )


async def main() -> None:
    with TemporaryDirectory(prefix="agent-company-provider-") as temporary:
        provider = LocalProvider()
        engine = MissionEngine(
            store=SQLiteStore(Path(temporary) / "state.sqlite3"),
            providers={"fast": provider},
        )
        mission = engine.create_mission(
            MissionCreate(title="Custom provider", objective="Return a typed local response")
        )
        result = await engine.run_mission(mission.id)
        print(result.status.value, result.summary)


if __name__ == "__main__":
    asyncio.run(main())
