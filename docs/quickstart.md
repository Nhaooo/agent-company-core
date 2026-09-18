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

     
`doctor` performs local checks without making provider network requests.

It checks:

- Whether the runtime directory can be created and written.
- Whether optional integration packages are installed.
- Whether supported provider environment variables are present.
- Whether configured provider base URLs use `http://` or `https://`.
- Whether a non-empty model identifier is supplied when provider settings are
  explicitly configured.
- Whether the local SQLite store can be initialized.

### Configuration trust boundaries

`doctor` reports credentials only as `set` or `not set`. It never prints API
key values or other credential contents.

The configuration checks are provider-neutral and local. They validate the
shape of explicitly supplied configuration, but they do not contact OpenAI,
Anthropic, Google, Ollama, or another model service to test credentials or
network connectivity.

A local Ollama-style configuration can therefore be checked without a cloud
API key, for example:

```powershell
$env:OLLAMA_BASE_URL="http://127.0.0.1:11434/v1"
$env:OLLAMA_MODEL="llama3.2"
agent-company doctor