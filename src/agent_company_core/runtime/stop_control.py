"""Persistent STOP control shared by model, tool, and mission execution."""

import json
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock


class StopRequested(RuntimeError):
    """Raised when execution is not allowed to continue."""


class StopControl:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def _read(self) -> dict[str, str | bool]:
        if not self.path.exists():
            return {"stopped": False, "reason": ""}
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"stopped": True, "reason": "unreadable stop state"}
        return {
            "stopped": bool(value.get("stopped", False)),
            "reason": str(value.get("reason", "")),
        }

    def request(self, reason: str = "requested") -> None:
        with self._lock:
            temporary = self.path.with_suffix(self.path.suffix + ".tmp")
            temporary.write_text(
                json.dumps(
                    {"stopped": True, "reason": reason, "at": datetime.now(UTC).isoformat()}
                ),
                encoding="utf-8",
            )
            temporary.replace(self.path)

    def clear(self) -> None:
        with self._lock:
            temporary = self.path.with_suffix(self.path.suffix + ".tmp")
            temporary.write_text(json.dumps({"stopped": False, "reason": ""}), encoding="utf-8")
            temporary.replace(self.path)

    def is_stopped(self) -> bool:
        with self._lock:
            return bool(self._read()["stopped"])

    def reason(self) -> str:
        with self._lock:
            return str(self._read()["reason"])

    def assert_running(self) -> None:
        if self.is_stopped():
            raise StopRequested(self.reason() or "execution stopped")
