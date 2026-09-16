# Examples

The examples are small, focused workflows. Offline examples use the fake model
and provider-shaped examples inject mock clients by default.

| Example | Demonstrates | Default requirement |
| --- | --- | --- |
| `basic.py` | create and run a mission | core package |
| `human_approval/` | exact human approval | core package |
| `stop_recovery/` | persistent STOP and recovery | core package |
| `capability_delegation/` | neutral capability selection | core package |
| `custom_tool/` | tool policy and audit | core package |
| `custom_provider/` | provider protocol | core package |
| `anthropic_claude/` | Claude adapter and typed response | core package; SDK only for live |
| `openai_compatible/` | compatible endpoint configuration | core package; SDK only for live |
| `local_ollama/` | local zero-paid-API path | core package; Ollama only for live |
| `fastapi_integration/` | reference HTTP app | `agent-company-core[app]` |
| `research_team/` | planner/researcher/reviewer missions | core package |

Run an example from the repository root with `python examples/.../main.py`.
Each directory README describes expected behavior and live prerequisites.
