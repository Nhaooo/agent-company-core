# Contributing

Contributions are welcome while the project is alpha. Start with a focused
issue when a change affects the public API, persistence semantics, provider
contracts, or security boundaries. Small documentation and test improvements
are welcome without prior design discussion.

## Local setup

Requirements: Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).

```powershell
git clone https://github.com/Nhaooo/agent-company-core.git
cd agent-company-core
uv sync --all-extras --dev
```

The full optional install is useful for integration work. Core tests do not
need cloud credentials, a running service, Docker, or network access after
dependencies are installed.

## Required checks

```powershell
uv run pytest
uv run ruff check src tests scripts
uv run mypy src
uv build
uv run twine check dist/*
uv run pip-audit
```

Provider tests must use injected fake clients. Do not make paid or credentialed
calls in CI. Do not commit `.env` files, runtime state, local paths, generated
artifacts, API keys, or provider response dumps.

## Architecture in one page

Read [the architecture guide](docs/development/architecture.md) first. In
short, typed contracts describe missions and model intentions; `MissionEngine`
composes persistence, routing, policy, STOP, memory, tools, and audit; provider
adapters implement only the neutral `ModelProvider` protocol.

Keep the core dependency-light and provider-neutral. Message text must not
become a hidden business router.

## Adding a provider

1. Add the adapter under `src/agent_company_core/integrations/`.
2. Import the SDK lazily so `import agent_company_core` remains lightweight.
3. Read credentials from the provider's standard environment/configuration
   chain; never hardcode or print them.
4. Accept an injected client for deterministic tests.
5. Normalize configuration, timeout, transport, and malformed structured
   response errors without copying provider response text into audit events.
6. Add success, structured output, error, timeout, missing configuration,
   fallback, and STOP tests.
7. Add a provider guide and a mocked-by-default example.

## Adding a store

Preserve the mission contract, idempotency behavior, event ordering, and
checkpoint semantics. Add conformance tests and document transaction,
durability, migration, and concurrency assumptions. A new database must be an
explicit optional extra; do not make a server mandatory for the offline path.

## Adding an integration

Keep host-specific SDKs behind an optional extra and a narrow module. State
clearly whether the integration is a gateway, a full implementation, or an
extension point. Do not imply Temporal or PostgreSQL guarantees that the code
does not provide.

## Pull requests

PRs should explain the behavior, compatibility impact, security implications,
provider assumptions, and test evidence. Prefer several coherent commits while
developing; the maintainers may squash on merge. Documentation should include
the smallest runnable example that teaches the new behavior.

## Security reports

Do not disclose an unpatched vulnerability in a public issue. Use GitHub's
private vulnerability reporting channel when enabled, or contact the
maintainer privately through the [Nhaooo GitHub profile](https://github.com/Nhaooo).
Never include credentials or sensitive production data in a report.
