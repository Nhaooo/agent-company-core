"""The small, offline-first ``agent-company`` command-line interface."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from agent_company_core import (
    AgentDecision,
    DecisionAction,
    FakeModel,
    MissionCreate,
    MissionEngine,
    ModelRequest,
    ModelResponse,
    RiskLevel,
    __version__,
)
from agent_company_core.persistence import SQLiteStore


def _data_dir(value: str | None = None) -> Path:
    return Path(value or os.environ.get("AGENT_COMPANY_DATA_DIR", "./runtime")).expanduser()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-company",
        description="Durable, provider-neutral multi-agent workflow tools.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser(
        "doctor", help="inspect local runtime and provider configuration"
    )
    doctor.add_argument("--data-dir", help="runtime directory (default: ./runtime)")
    doctor.set_defaults(handler=_doctor)

    demo = subparsers.add_parser("demo", help="run the deterministic offline workflow demo")
    demo.set_defaults(handler=_demo)

    init = subparsers.add_parser("init", help="scaffold a minimal starter project")
    init.add_argument("path", help="directory to create")
    init.set_defaults(handler=_init)

    run = subparsers.add_parser("run", help="run one objective with the offline fake model")
    run.add_argument("objective", help="objective for the durable mission")
    run.add_argument("--title", default="CLI mission", help="mission title")
    run.add_argument("--data-dir", help="runtime directory (default: ./runtime)")
    run.set_defaults(handler=_run)
    return parser


def _module_status(module: str) -> str:
    try:
        return "installed" if importlib.util.find_spec(module) else "not installed"
    except (ImportError, ModuleNotFoundError, ValueError):
        return "not installed"


def _doctor(args: argparse.Namespace) -> int:
    data_dir = _data_dir(args.data_dir)
    print(f"agent-company {__version__}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Runtime directory: {data_dir}")

    writable = False
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        probe = data_dir / ".write-check"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        writable = True
    except OSError:
        pass
    print(f"Writable runtime directory: {'yes' if writable else 'no'}")

    print("Optional integrations:")
    for label, module in (
        ("Anthropic", "anthropic"),
        ("OpenAI-compatible", "openai"),
        ("Google", "google.genai"),
        ("Temporal", "temporalio"),
        ("PostgreSQL", "sqlalchemy"),
        ("FastAPI reference", "fastapi"),
    ):
        print(f"  {label}: {_module_status(module)}")

    print("Provider configuration (presence only):")
    for variable in (
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "GOOGLE_API_KEY",
        "GOOGLE_CLOUD_PROJECT",
    ):
        print(f"  {variable}: {'set' if os.environ.get(variable) else 'not set'}")

    database_ready = False
    try:
        missions = SQLiteStore(data_dir / "state.sqlite3").list_missions()
        database_ready = True
        print(f"SQLite store: ready ({len(missions)} missions)")
    except (OSError, RuntimeError):
        print("SQLite store: unavailable")
    return 0 if writable and database_ready else 1


class _ApprovalDemoModel:
    name = "demo-approval"

    async def complete(self, request: ModelRequest) -> ModelResponse:
        decision = AgentDecision(
            action=DecisionAction.REQUEST_APPROVAL,
            rationale="the demo pauses before a consequential effect",
            risk=RiskLevel.HIGH,
            tool_name="publish-demo",
        )
        return ModelResponse(
            text=decision.model_dump_json(),
            model="demo-approval",
            provider=self.name,
            structured=decision,
        )


async def _run_demo() -> None:
    with tempfile.TemporaryDirectory(prefix="agent-company-demo-") as temporary:
        root = Path(temporary)
        store = SQLiteStore(root / "state.sqlite3")
        fake = FakeModel("offline review completed")
        engine = MissionEngine(
            store=store,
            providers={"fast": fake, "reasoning": fake, "vision": fake},
        )

        mission = engine.create_mission(
            MissionCreate(
                title="Offline research mission",
                objective="Review a harmless local note and summarize the result",
            )
        )
        print("1. created durable mission       status=received")
        delegated = engine.delegate_mission(mission.id, capabilities={"research"})
        print(f"2. delegated by capability        agent={delegated.assigned_agents[0]}")
        result = await engine.run_mission(mission.id)
        print(f"3. FakeModel typed decision       status={result.status.value}")

        event_count = len(store.events(mission.id))
        print(f"4. redacted audit trail           events={event_count}")
        reopened = MissionEngine(store=SQLiteStore(root / "state.sqlite3"))
        persisted = reopened.get_mission(mission.id)
        print(f"5. reopened persistent state      status={persisted.status.value}")

        approval_engine = MissionEngine(
            store=store,
            providers={"fast": _ApprovalDemoModel()},
            stop=engine.stop,
            audit=engine.audit,
            memory=engine.memory,
        )
        approval_mission = approval_engine.create_mission(
            MissionCreate(title="Approval boundary", objective="Demonstrate a pause")
        )
        approval = await approval_engine.run_mission(approval_mission.id)
        print(f"6. human approval boundary        status={approval.status.value}")

        stopped_mission = engine.create_mission(
            MissionCreate(title="STOP boundary", objective="Demonstrate operator control")
        )
        engine.request_stop("operator requested stop")
        stopped = await engine.run_mission(stopped_mission.id)
        print(f"7. persistent STOP boundary       status={stopped.status.value}")
        print("Demo complete: offline, deterministic, no credentials or network.")


def _demo(args: argparse.Namespace) -> int:
    del args
    asyncio.run(_run_demo())
    return 0


async def _run_objective(args: argparse.Namespace) -> None:
    data_dir = _data_dir(args.data_dir)
    engine = MissionEngine(store=SQLiteStore(data_dir / "state.sqlite3"))
    mission = engine.create_mission(MissionCreate(title=args.title, objective=args.objective))
    result = await engine.run_mission(mission.id)
    print(result.model_dump_json(indent=2))


def _run(args: argparse.Namespace) -> int:
    asyncio.run(_run_objective(args))
    return 0


_STARTER_PYPROJECT = """[project]
name = \"my-agent-app\"
version = \"0.1.0\"
requires-python = \">=3.11\"
dependencies = [\"agent-company-core>=0.2,<0.3\"]

[build-system]
requires = [\"setuptools>=68\"]
build-backend = \"setuptools.build_meta\"
"""

_STARTER_MAIN = '''"""A minimal durable agent-company-core application."""

import asyncio
from pathlib import Path

from agent_company_core import MissionCreate, MissionEngine
from agent_company_core.persistence import SQLiteStore


async def main() -> None:
    engine = MissionEngine(store=SQLiteStore(Path("runtime/state.sqlite3")))
    mission = engine.create_mission(
        MissionCreate(title="Starter mission", objective="Complete a harmless local task")
    )
    result = await engine.run_mission(mission.id)
    print(result.status.value, result.summary)


if __name__ == "__main__":
    asyncio.run(main())
'''

_STARTER_README = """# my-agent-app

Minimal starter project using `agent-company-core` with its offline FakeModel.

```powershell
python -m pip install -e .
python main.py
```

The generated example needs no API key or network access. Replace the model
provider in `main.py` when you are ready to connect an optional provider.
"""


def _init(args: argparse.Namespace) -> int:
    target = Path(args.path).expanduser()
    if target.exists() and any(target.iterdir()):
        print(f"error: target directory is not empty: {target}", file=sys.stderr)
        return 2
    target.mkdir(parents=True, exist_ok=True)
    for name, content in (
        ("pyproject.toml", _STARTER_PYPROJECT),
        ("main.py", _STARTER_MAIN),
        ("README.md", _STARTER_README),
        (".gitignore", "runtime/\n__pycache__/\n*.pyc\n"),
    ):
        (target / name).write_text(content, encoding="utf-8")
    print(f"Created starter project: {target}")
    print("Next: python -m pip install -e . && python main.py")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


__all__ = ["main"]
