# Contributing

Contributions are welcome while the project is alpha. Please open an issue
before a large design change so the public API and security boundaries can be
discussed.

## Local setup

```powershell
uv venv
uv pip install -e ".[dev,app]"
python -m pytest
ruff check src tests
mypy src
```

Keep the core dependency-light and provider-neutral. New effects should be
behind an interface, carry explicit risk metadata, check STOP, and emit an
auditable event. Do not add routing based on message keywords. Tests must run
without network access, cloud credentials, or paid APIs.

## Pull requests

Explain the behavioral change, tests run, security implications, and any
provider-specific assumptions. Avoid committing `.env` files, runtime state,
credentials, or generated artifacts.
