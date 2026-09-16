"""Minimal localhost reference application using only the fake provider."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, cast
from uuid import UUID

from agent_company_core.contracts import MissionCreate
from agent_company_core.models import FakeModel, RoutingAssessment
from agent_company_core.orchestration import MissionEngine
from agent_company_core.persistence import SQLiteStore
from agent_company_core.tools import ToolRegistry, ToolSpec


def _data_dir() -> Path:
    return Path(os.environ.get("AGENT_COMPANY_DATA_DIR", "./runtime")).expanduser()


def build_engine(data_dir: str | Path | None = None) -> MissionEngine:
    root = Path(data_dir) if data_dir is not None else _data_dir()
    root.mkdir(parents=True, exist_ok=True)
    tools = ToolRegistry()

    def echo(arguments: dict[str, object]) -> dict[str, object]:
        return {"echo": arguments.get("value", "")}

    tools.register(ToolSpec("echo", "Return a supplied value", frozenset({"text"}), echo))
    model = FakeModel("The reference model completed the requested turn.")
    return MissionEngine(
        store=SQLiteStore(root / "state.sqlite3"),
        providers={"fast": model, "reasoning": model, "vision": model},
        tools=tools,
    )


def create_app(data_dir: str | Path | None = None) -> Any:
    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise RuntimeError("install agent-company-core[app] to use the reference app") from exc

    engine = build_engine(data_dir)
    app = FastAPI(title="Agent Company Core reference", version="0.1.0")

    @app.get("/")
    async def index() -> dict[str, object]:
        return {"name": "agent-company-core reference", "status": "alpha", "docs": "/docs"}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "provider": "fake"}

    @app.post("/chat")
    async def chat(payload: dict[str, object]) -> dict[str, object]:
        text = str(payload.get("message", "")).strip()
        if not text:
            return {"response": "message is required"}
        mission = engine.create_mission(MissionCreate(title="Conversation turn", objective=text))
        result = await engine.run_mission(mission.id)
        return cast(dict[str, object], result.model_dump(mode="json"))

    @app.post("/missions")
    async def create_mission(payload: MissionCreate) -> dict[str, object]:
        return cast(dict[str, object], engine.create_mission(payload).model_dump(mode="json"))

    @app.get("/missions")
    async def list_missions() -> list[dict[str, object]]:
        return [
            cast(dict[str, object], mission.model_dump(mode="json"))
            for mission in engine.list_missions()
        ]

    @app.post("/missions/{mission_id}/run")
    async def run_mission(
        mission_id: UUID, payload: dict[str, object] | None = None
    ) -> dict[str, object]:
        values = payload or {}
        assessment = RoutingAssessment.model_validate(
            values.get(
                "assessment", {"complexity": 0.3, "ambiguity": 0.1, "risk": 0.1, "continuity": 0.2}
            )
        )
        raw_capabilities = values.get("capabilities", [])
        capabilities = (
            {str(item) for item in raw_capabilities}
            if isinstance(raw_capabilities, list)
            else set()
        )
        result = await engine.run_mission(
            mission_id, assessment=assessment, capabilities=capabilities
        )
        return cast(dict[str, object], result.model_dump(mode="json"))

    @app.post("/runtime/stop")
    async def stop(payload: dict[str, object] | None = None) -> dict[str, str]:
        engine.request_stop(str((payload or {}).get("reason", "requested")))
        return {"status": "stopped"}

    @app.post("/runtime/clear-stop")
    async def clear_stop() -> dict[str, str]:
        engine.clear_stop()
        return {"status": "running"}

    @app.post("/memory")
    async def remember(payload: dict[str, object]) -> dict[str, object]:
        item = engine.remember(
            str(payload["content"]),
            scope=str(payload.get("scope", "default")),
            key=str(payload["key"]) if payload.get("key") else None,
        )
        return {"id": str(item.id), "scope": item.scope}

    @app.get("/memory/search")
    async def search_memory(q: str, scope: str | None = None) -> list[dict[str, object]]:
        return [
            {"id": str(item.id), "content": item.content, "scope": item.scope}
            for item in engine.search_memory(q, scope=scope)
        ]

    @app.get("/tools")
    async def tools() -> list[dict[str, object]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "capabilities": sorted(tool.capabilities),
                "risk": tool.risk.value,
            }
            for tool in engine.tools.list()
        ]

    return app


app = create_app()


def main() -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("install agent-company-core[app] to run the reference app") from exc
    uvicorn.run(
        "agent_company_core.reference.app:app",
        host=os.environ.get("AGENT_COMPANY_HOST", "127.0.0.1"),
        port=int(os.environ.get("AGENT_COMPANY_PORT", "8000")),
        reload=False,
    )
