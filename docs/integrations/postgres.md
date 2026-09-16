# PostgreSQL

```powershell
python -m pip install "agent-company-core[postgres]"
```

Version 0.2.0 retains a dependency check and extension boundary for
SQLAlchemy/asyncpg. The durable default is SQLite and a full PostgreSQL mission
repository is not shipped yet. See the open contributor issue for the intended
contract and migration-test scope.
