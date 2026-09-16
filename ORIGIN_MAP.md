# Origin map

This map records concepts, not copied private files or private operational
content. The target repository was initialized with a fresh Git history.

| Public module | Conceptual source area | Public adaptation |
| --- | --- | --- |
| `contracts/mission.py` | private mission/domain contracts | neutral lifecycle, event, idempotency, and checkpoint types |
| `contracts/decision.py` | private decision contract | generic typed intention with no persona identity |
| `models/` | private routing/runtime model layer | provider protocol, fake provider, and structured route assessment |
| `agents/registry.py` | private agent registry | three neutral demo agents selected by capabilities |
| `permissions/` | private permission and risk layer | exact-match approval boundary over structured actions |
| `runtime/stop_control.py` | private STOP control | local persistent operator signal with explicit limits |
| `persistence/sqlite.py` | private durable mission repositories | small local implementation behind a replaceable boundary |
| `memory/store.py` | private memory abstractions | scope-aware persistent interface without private content |
| `skills/runner.py` | private skill runner | restricted experimental runner with opt-in trust model |
| `observability/` | private audit/redaction utilities | generic redacted JSONL audit logger |
| `orchestration/engine.py` | private mission workflow concepts | compact composition of the public interfaces |

Private personas, prompts, configuration, local paths, reports, logs, vaults,
artifacts, and internal planning documents were intentionally excluded.
