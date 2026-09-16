"""Demonstrate persistent STOP and explicit recovery."""

from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_company_core import MissionCreate, MissionEngine
from agent_company_core.models import FakeModel
from agent_company_core.persistence import SQLiteStore


async def main() -> None:
    with TemporaryDirectory(prefix="agent-company-stop-") as temporary:
        root = Path(temporary)
        model = FakeModel("recovered offline")
        engine = MissionEngine(
            store=SQLiteStore(root / "state.sqlite3"),
            providers={"fast": model, "reasoning": model, "vision": model},
        )
        mission = engine.create_mission(
            MissionCreate(title="Recoverable mission", objective="Resume a harmless task")
        )
        engine.request_stop("operator maintenance")
        stopped = await engine.run_mission(mission.id)
        print("stopped:", stopped.status.value, "provider calls:", len(model.requests))
        engine.clear_stop()
        engine.resume_mission(mission.id)
        recovered = await engine.run_mission(mission.id)
        print("recovered:", recovered.status.value, recovered.summary)


if __name__ == "__main__":
    asyncio.run(main())
