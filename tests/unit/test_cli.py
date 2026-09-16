from pathlib import Path

from agent_company_core.cli import main


def test_cli_demo_is_offline_and_teaches_boundaries(capsys) -> None:
    assert main(["demo"]) == 0
    output = capsys.readouterr().out
    assert "FakeModel typed decision       status=completed" in output
    assert "human approval boundary        status=waiting_approval" in output
    assert "persistent STOP boundary       status=stopped" in output
    assert "no credentials or network" in output


def test_cli_doctor_reports_presence_without_values(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-print")
    assert main(["doctor", "--data-dir", str(tmp_path)]) == 0
    output = capsys.readouterr().out
    assert "OPENAI_API_KEY: set" in output
    assert "must-not-print" not in output
    assert "SQLite store: ready" in output


def test_cli_init_creates_small_runnable_project(tmp_path: Path, capsys) -> None:
    target = tmp_path / "starter"

    assert main(["init", str(target)]) == 0

    assert (target / "main.py").is_file()
    assert (target / "pyproject.toml").is_file()
    assert "MissionEngine" in (target / "main.py").read_text(encoding="utf-8")
    assert "agent-company-core>=0.2,<0.3" in (target / "pyproject.toml").read_text(encoding="utf-8")
    assert "Created starter project" in capsys.readouterr().out
