# Provider matrix

The core only depends on Pydantic. Optional SDKs are imported when their
adapter is constructed, so offline core tests do not need provider accounts.

| Provider | Status in 0.2.0 | Install | Typed decision path | Test mode |
| --- | --- | --- | --- | --- |
| `FakeModel` | shipped | no extra | built-in Pydantic fixture | deterministic |
| Anthropic Claude | shipped, optional | `agent-company-core[anthropic]` | JSON response + Pydantic validation | injected fake client |
| OpenAI-compatible | shipped, optional | `agent-company-core[openai]` | JSON response + Pydantic validation | injected fake client |
| Ollama | via OpenAI-compatible | `agent-company-core[openai]` | same as compatible adapter | mocked by default |
| Google Gen AI | existing optional adapter | `agent-company-core[google]` | SDK parsed response | boundary tests |
| Temporal | client gateway only | `agent-company-core[temporal]` | host-owned workflows | no server in CI |
| PostgreSQL | extension boundary only | `agent-company-core[postgres]` | host-owned repository | no server in CI |

Live provider calls are opt-in and are not required by CI. Model IDs are
application configuration. Providers can retire or rename models; check their
current catalogs before deploying.
