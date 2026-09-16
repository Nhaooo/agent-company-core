from pathlib import Path

import pytest

from agent_company_core.observability import REDACTED, AuditLogger, redact
from agent_company_core.runtime import StopControl, StopRequested


def test_redaction_is_recursive() -> None:
    value = redact(
        {
            "api_key": "do-not-print",
            "nested": [{"token": "also-private"}],
            "text": "Bearer abcdefghijklmnop",
        }
    )
    assert value["api_key"] == REDACTED
    assert value["nested"][0]["token"] == REDACTED
    assert REDACTED in value["text"]


def test_stop_is_persistent(tmp_path: Path) -> None:
    path = tmp_path / "stop.json"
    control = StopControl(path)
    control.request("maintenance")
    with pytest.raises(StopRequested):
        control.assert_running()
    assert StopControl(path).reason() == "maintenance"
    StopControl(path).clear()
    StopControl(path).assert_running()


def test_audit_logger_does_not_write_secret(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    AuditLogger(path).record("test", payload={"password": "hidden"})
    assert "hidden" not in path.read_text(encoding="utf-8")
