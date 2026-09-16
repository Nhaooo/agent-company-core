"""Small durable SQLite store used by the reference runtime.

SQLite is intentionally the default: it keeps the core runnable locally while
the storage interfaces leave room for PostgreSQL implementations.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from agent_company_core.contracts import Mission, MissionCreate, MissionEvent, MissionStatus


def _now() -> str:
    return datetime.now(UTC).isoformat()


class SQLiteStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS missions (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, objective TEXT NOT NULL,
                    status TEXT NOT NULL, owner TEXT NOT NULL, assigned_agents TEXT NOT NULL,
                    priority INTEGER NOT NULL, idempotency_key TEXT UNIQUE, checkpoint TEXT,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS mission_events (
                    id TEXT PRIMARY KEY, mission_id TEXT NOT NULL REFERENCES missions(id),
                    event_type TEXT NOT NULL, payload TEXT NOT NULL, sequence INTEGER NOT NULL,
                    created_at TEXT NOT NULL, UNIQUE(mission_id, sequence)
                );
                CREATE TABLE IF NOT EXISTS approvals (
                    id TEXT PRIMARY KEY, mission_id TEXT, action TEXT NOT NULL,
                    target TEXT NOT NULL,
                    arguments TEXT NOT NULL, risk TEXT NOT NULL, requested_by TEXT NOT NULL,
                    request_hash TEXT NOT NULL, expires_at TEXT NOT NULL, status TEXT NOT NULL,
                    resolved_by TEXT, resolved_hash TEXT, resolved_arguments TEXT
                );
                """
            )

    @staticmethod
    def _mission(row: sqlite3.Row) -> Mission:
        return Mission(
            id=UUID(row["id"]),
            title=row["title"],
            objective=row["objective"],
            status=MissionStatus(row["status"]),
            owner=row["owner"],
            assigned_agents=json.loads(row["assigned_agents"]),
            priority=row["priority"],
            idempotency_key=row["idempotency_key"],
            checkpoint=row["checkpoint"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def create_mission(self, value: MissionCreate) -> Mission:
        with self._connect() as db:
            if value.idempotency_key:
                row = db.execute(
                    "SELECT * FROM missions WHERE idempotency_key = ?", (value.idempotency_key,)
                ).fetchone()
                if row:
                    return self._mission(row)
            mission = Mission(
                title=value.title,
                objective=value.objective,
                owner=value.owner,
                priority=value.priority,
                idempotency_key=value.idempotency_key,
            )
            db.execute(
                "INSERT INTO missions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(mission.id),
                    mission.title,
                    mission.objective,
                    mission.status.value,
                    mission.owner,
                    json.dumps(mission.assigned_agents),
                    mission.priority,
                    mission.idempotency_key,
                    mission.checkpoint,
                    mission.created_at.isoformat(),
                    mission.updated_at.isoformat(),
                ),
            )
            self._append_event(db, mission.id, "mission.created", {"title": mission.title})
            return mission

    def get_mission(self, mission_id: UUID) -> Mission:
        with self._connect() as db:
            row = db.execute("SELECT * FROM missions WHERE id = ?", (str(mission_id),)).fetchone()
            if not row:
                raise KeyError(f"unknown mission: {mission_id}")
            return self._mission(row)

    def list_missions(self) -> list[Mission]:
        with self._connect() as db:
            return [
                self._mission(row)
                for row in db.execute("SELECT * FROM missions ORDER BY created_at DESC")
            ]

    def set_status(
        self, mission_id: UUID, status: MissionStatus, *, payload: dict[str, object] | None = None
    ) -> Mission:
        now = _now()
        with self._connect() as db:
            db.execute(
                "UPDATE missions SET status = ?, updated_at = ? WHERE id = ?",
                (status.value, now, str(mission_id)),
            )
            self._append_event(db, mission_id, f"mission.{status.value}", payload or {})
            row = db.execute("SELECT * FROM missions WHERE id = ?", (str(mission_id),)).fetchone()
            if not row:
                raise KeyError(f"unknown mission: {mission_id}")
            return self._mission(row)

    def assign_agents(self, mission_id: UUID, agent_ids: list[str]) -> Mission:
        now = _now()
        with self._connect() as db:
            db.execute(
                "UPDATE missions SET assigned_agents = ?, updated_at = ? WHERE id = ?",
                (json.dumps(agent_ids), now, str(mission_id)),
            )
            self._append_event(db, mission_id, "mission.delegated", {"agent_ids": agent_ids})
            row = db.execute("SELECT * FROM missions WHERE id = ?", (str(mission_id),)).fetchone()
            if not row:
                raise KeyError(f"unknown mission: {mission_id}")
            return self._mission(row)

    def checkpoint(self, mission_id: UUID, value: str) -> Mission:
        now = _now()
        with self._connect() as db:
            db.execute(
                "UPDATE missions SET checkpoint = ?, updated_at = ? WHERE id = ?",
                (value, now, str(mission_id)),
            )
            self._append_event(db, mission_id, "mission.checkpointed", {"checkpoint": value})
            row = db.execute("SELECT * FROM missions WHERE id = ?", (str(mission_id),)).fetchone()
            if not row:
                raise KeyError(f"unknown mission: {mission_id}")
            return self._mission(row)

    def _append_event(
        self, db: sqlite3.Connection, mission_id: UUID, event_type: str, payload: dict[str, object]
    ) -> MissionEvent:
        sequence = int(
            db.execute(
                "SELECT COALESCE(MAX(sequence), 0) + 1 FROM mission_events WHERE mission_id = ?",
                (str(mission_id),),
            ).fetchone()[0]
        )
        event = MissionEvent(
            mission_id=mission_id, event_type=event_type, payload=payload, sequence=sequence
        )
        db.execute(
            "INSERT INTO mission_events VALUES (?, ?, ?, ?, ?, ?)",
            (
                str(event.id),
                str(event.mission_id),
                event.event_type,
                json.dumps(event.payload, sort_keys=True),
                event.sequence,
                event.created_at.isoformat(),
            ),
        )
        return event

    def events(self, mission_id: UUID) -> list[MissionEvent]:
        with self._connect() as db:
            return [
                MissionEvent(
                    id=UUID(row["id"]),
                    mission_id=mission_id,
                    event_type=row["event_type"],
                    payload=json.loads(row["payload"]),
                    sequence=row["sequence"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in db.execute(
                    "SELECT * FROM mission_events WHERE mission_id = ? ORDER BY sequence",
                    (str(mission_id),),
                )
            ]

    def save_approval(self, request: Any) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO approvals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(request.id),
                    str(request.mission_id) if request.mission_id else None,
                    request.action,
                    request.target,
                    json.dumps(request.arguments, sort_keys=True),
                    request.risk.value,
                    request.requested_by,
                    request.request_hash,
                    request.expires_at.isoformat(),
                    "pending",
                    None,
                    None,
                    None,
                ),
            )

    def get_approval(self, approval_id: UUID) -> dict[str, Any]:
        with self._connect() as db:
            row = db.execute("SELECT * FROM approvals WHERE id = ?", (str(approval_id),)).fetchone()
            if not row:
                raise KeyError(f"unknown approval: {approval_id}")
            return dict(row)

    def list_approvals(self, mission_id: UUID | None = None) -> list[dict[str, Any]]:
        with self._connect() as db:
            if mission_id is None:
                rows = db.execute("SELECT * FROM approvals ORDER BY expires_at").fetchall()
            else:
                rows = db.execute(
                    "SELECT * FROM approvals WHERE mission_id = ? ORDER BY expires_at",
                    (str(mission_id),),
                ).fetchall()
            return [dict(row) for row in rows]

    def resolve_approval(
        self,
        approval_id: UUID,
        *,
        approved: bool,
        resolved_by: str,
        request_hash: str,
        arguments: dict[str, object] | None = None,
    ) -> None:
        with self._connect() as db:
            db.execute(
                "UPDATE approvals SET status = ?, resolved_by = ?, resolved_hash = ?, "
                "resolved_arguments = ? WHERE id = ? AND status = 'pending'",
                (
                    "approved" if approved else "rejected",
                    resolved_by,
                    request_hash,
                    json.dumps(arguments, sort_keys=True) if arguments is not None else None,
                    str(approval_id),
                ),
            )
