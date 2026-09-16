"""Append-only JSONL audit logging with recursive redaction."""

import json
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any, cast
from uuid import uuid4

from .redaction import redact


class AuditLogger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def record(
        self,
        event_type: str,
        *,
        payload: dict[str, Any] | None = None,
        mission_id: str | None = None,
    ) -> dict[str, Any]:
        event = redact(
            {
                "id": str(uuid4()),
                "at": datetime.now(UTC).isoformat(),
                "event_type": event_type,
                "mission_id": mission_id,
                "payload": payload or {},
            }
        )
        with self._lock, self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")
        return cast(dict[str, Any], event)
