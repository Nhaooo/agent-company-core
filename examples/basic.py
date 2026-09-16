"""A no-credential durable workflow."""

import asyncio
from pathlib import Path

from agent_company_core import MissionCreate, MissionEngine
from agent_company_core.persistence import SQLiteStore


async def main() -> None:
    engine = MissionEngine(store=SQLiteStore(Path("runtime/state.sqlite3")))
    mission = engine.create_mission(
        MissionCreate(title="Example", objective="Review a small input")
    )
    result = await engine.run_mission(mission.id)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
