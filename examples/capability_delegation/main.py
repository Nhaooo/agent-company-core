"""Select an agent by a declared capability."""

from pathlib import Path
from tempfile import TemporaryDirectory

from agent_company_core import MissionCreate, MissionEngine
from agent_company_core.persistence import SQLiteStore


def main() -> None:
    with TemporaryDirectory(prefix="agent-company-delegation-") as temporary:
        engine = MissionEngine(store=SQLiteStore(Path(temporary) / "state.sqlite3"))
        mission = engine.create_mission(
            MissionCreate(title="Evidence task", objective="Prepare a harmless evidence review")
        )
        delegated = engine.delegate_mission(mission.id, capabilities={"research", "evidence"})
        print("delegated agents:", ", ".join(delegated.assigned_agents))
        print("status:", delegated.status.value)


if __name__ == "__main__":
    main()
