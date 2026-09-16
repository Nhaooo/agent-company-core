# Anthropic Claude

Install the optional SDK extra:

```powershell
python -m pip install "agent-company-core[anthropic]"
$env:ANTHROPIC_API_KEY = "..."
```

The adapter uses the official async Anthropic Messages API and the standard
`ANTHROPIC_API_KEY` environment variable. The model identifier is required at
construction time. Anthropic currently documents `claude-sonnet-4-6` as an
active example; keep it configurable and check Anthropic's model lifecycle
documentation before deploying.

```python
import asyncio
import os
from pathlib import Path

from agent_company_core import AnthropicModel, MissionCreate, MissionEngine
from agent_company_core.persistence import SQLiteStore


async def main() -> None:
    model = AnthropicModel(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    )
    engine = MissionEngine(
        store=SQLiteStore(Path("runtime/state.sqlite3")),
        providers={"fast": model, "reasoning": model, "vision": model},
    )
    mission = engine.create_mission(
        MissionCreate(title="Claude mission", objective="Return a harmless typed decision")
    )
    result = await engine.run_mission(mission.id)
    print(result.status.value, result.summary)


asyncio.run(main())
```

The framework asks the model for JSON when a response schema is supplied, then
validates the result as `AgentDecision`. Provider failures are normalized so
the engine can use its declared fallback aliases. The adapter never writes the
API key to audit output or exception text.

The repository example is safe by default: it injects a fake client and makes
no paid call. Use `--live` only in a controlled local environment with an
explicitly configured key.
