from pathlib import Path

from agent_company_core import MissionCreate, MissionStatus
from agent_company_core.memory import MemoryItem, SQLiteMemoryStore
from agent_company_core.persistence import SQLiteStore


def test_mission_idempotency_and_event_sequence(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "state.sqlite3")
    request = MissionCreate(title="Build", objective="An objective", idempotency_key="same")
    first = store.create_mission(request)
    second = store.create_mission(request)
    assert first.id == second.id
    store.set_status(first.id, MissionStatus.QUEUED)
    store.set_status(first.id, MissionStatus.RUNNING)
    assert [event.sequence for event in store.events(first.id)] == [1, 2, 3]


def test_memory_survives_new_store_instance(tmp_path: Path) -> None:
    path = tmp_path / "state.sqlite3"
    SQLiteMemoryStore(path).remember(MemoryItem(content="durable fact", scope="project"))
    matches = SQLiteMemoryStore(path).search("durable", scope="project")
    assert len(matches) == 1
