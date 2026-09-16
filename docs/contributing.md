# Contributing

Read the repository [contribution guide](https://github.com/Nhaooo/agent-company-core/blob/main/CONTRIBUTING.md), then run:

```powershell
uv sync --all-extras --dev
uv run pytest
uv run ruff check src tests scripts
uv run mypy src
uv build
```

Tests must remain credential-free and network-free. New effects require an
explicit interface, risk metadata, STOP checks, and an audit event. Provider
and storage changes should include a contract test and documentation.
