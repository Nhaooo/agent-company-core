from pathlib import Path

import pytest

from agent_company_core import MissionCreate, MissionStatus
from agent_company_core.models import FakeModel
from agent_company_core.orchestration import MissionEngine
from agent_company_core.persistence import SQLiteStore


@pytest.mark.asyncio
async def test_fake_model_workflow_is_durable(tmp_path: Path) -> None:
    path = tmp_path / "state.sqlite3"
    engine = MissionEngine(
        store=SQLiteStore(path),
        providers={
            "fast": FakeModel("finished"),
            "reasoning": FakeModel("finished"),
            "vision": FakeModel("finished"),
        },
    )
    mission = engine.create_mission(
        MissionCreate(title="Example", objective="Complete a harmless example")
    )
    result = await engine.run_mission(mission.id)
    assert result.status is MissionStatus.COMPLETED
    assert SQLiteStore(path).get_mission(mission.id).status is MissionStatus.COMPLETED


@pytest.mark.asyncio
async def test_stop_prevents_new_model_work(tmp_path: Path) -> None:
    model = FakeModel()
    engine = MissionEngine(
        store=SQLiteStore(tmp_path / "state.sqlite3"),
        providers={"fast": model, "reasoning": model, "vision": model},
    )
    mission = engine.create_mission(MissionCreate(title="Stopped", objective="Should not run"))
    engine.request_stop("operator request")
    result = await engine.run_mission(mission.id)
    assert result.status is MissionStatus.STOPPED
    assert not model.requests
