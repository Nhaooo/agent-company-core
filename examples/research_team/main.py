"""Run a harmless planner/researcher/reviewer workflow offline."""

from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

from agent_company_core import MissionCreate, MissionEngine
from agent_company_core.models import FakeModel
from agent_company_core.persistence import SQLiteStore


async def main() -> None:
    with TemporaryDirectory(prefix="agent-company-research-team-") as temporary:
        path = Path(temporary) / "state.sqlite3"
        fake = FakeModel("team step completed")
        engine = MissionEngine(
            store=SQLiteStore(path),
            providers={"fast": fake, "reasoning": fake, "vision": fake},
        )
        roles = (
            ("planner", "planning", "Break the harmless research objective into steps"),
            ("researcher", "research", "Collect harmless local evidence"),
            ("reviewer", "review", "Verify the team's harmless result"),
        )
        missions = []
        for role, capability, objective in roles:
            mission = engine.create_mission(MissionCreate(title=role, objective=objective))
            delegated = engine.delegate_mission(mission.id, capabilities={capability})
            result = await engine.run_mission(mission.id)
            missions.append(result)
            print(role, delegated.assigned_agents[0], result.status.value)
        reopened = SQLiteStore(path)
        print("durable completed:", all(item.status.value == "completed" for item in missions))
        print("stored missions:", len(reopened.list_missions()))
        print("audit events:", sum(len(reopened.events(item.mission_id)) for item in missions))


if __name__ == "__main__":
    asyncio.run(main())
