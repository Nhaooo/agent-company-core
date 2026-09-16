# Quickstart

## Install and run offline

```powershell
python -m pip install agent-company-core
agent-company demo
```

No cloud credentials, Docker, database server, or network call is required.

## Use the library

```python
import asyncio
from pathlib import Path

from agent_company_core import MissionCreate, MissionEngine
from agent_company_core.persistence import SQLiteStore


async def main() -> None:
    engine = MissionEngine(store=SQLiteStore(Path("runtime/state.sqlite3")))
    mission = engine.create_mission(
        MissionCreate(title="Review note", objective="Review a harmless local note")
    )
    result = await engine.run_mission(mission.id)
    print(result.status.value, result.summary)


asyncio.run(main())
```

The default `FakeModel` returns a deterministic typed response. Replace the
provider mapping only when the application is ready for a hosted or local
model.

## Inspect the local runtime

```powershell
agent-company doctor
agent-company init my-agent-app
```

`doctor` reports configuration presence, never configuration values.
