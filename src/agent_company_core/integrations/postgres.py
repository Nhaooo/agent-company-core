"""Optional PostgreSQL extension point.

The local reference implementation uses SQLite. Applications needing
PostgreSQL can implement the same repository methods behind this boundary.
"""

import importlib
from typing import Any


def require_sqlalchemy() -> Any:
    try:
        sqlalchemy = importlib.import_module("sqlalchemy")
    except ImportError as exc:
        raise RuntimeError("install agent-company-core[postgres] for PostgreSQL support") from exc
    return sqlalchemy
