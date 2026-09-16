from pathlib import Path

import pytest

from agent_company_core.orchestration import MissionEngine
from agent_company_core.persistence import SQLiteStore


@pytest.fixture
def engine(tmp_path: Path) -> MissionEngine:
    return MissionEngine(store=SQLiteStore(tmp_path / "state.sqlite3"))
