"""Persistent memory interface and SQLite implementation."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class MemoryItem:
    content: str
    scope: str = "default"
    key: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class MemoryStore:
    def remember(self, item: MemoryItem) -> MemoryItem:
        raise NotImplementedError

    def search(self, query: str, *, scope: str | None = None, limit: int = 10) -> list[MemoryItem]:
        raise NotImplementedError


class SQLiteMemoryStore(MemoryStore):
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS memories ("
                "id TEXT PRIMARY KEY, scope TEXT NOT NULL, key TEXT, content TEXT NOT NULL, "
                "metadata TEXT NOT NULL, created_at TEXT NOT NULL)"
            )

    def remember(self, item: MemoryItem) -> MemoryItem:
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute(
                "INSERT OR REPLACE INTO memories VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(item.id),
                    item.scope,
                    item.key,
                    item.content,
                    json.dumps(item.metadata, sort_keys=True),
                    item.created_at.isoformat(),
                ),
            )
        return item

    def search(self, query: str, *, scope: str | None = None, limit: int = 10) -> list[MemoryItem]:
        if not query.strip() or limit < 1:
            return []
        pattern = f"%{query.strip()}%"
        sql = "SELECT * FROM memories WHERE content LIKE ?"
        args: list[object] = [pattern]
        if scope is not None:
            sql += " AND scope = ?"
            args.append(scope)
        sql += " ORDER BY created_at DESC LIMIT ?"
        args.append(limit)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.row_factory = sqlite3.Row
            rows = db.execute(sql, args).fetchall()
        return [
            MemoryItem(
                content=row["content"],
                scope=row["scope"],
                key=row["key"],
                metadata=json.loads(row["metadata"]),
                id=UUID(row["id"]),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]
