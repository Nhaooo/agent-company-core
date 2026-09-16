"""Use the generic OpenAI-compatible adapter with an offline mock by default."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from agent_company_core import MissionCreate, MissionEngine, OpenAICompatibleModel
from agent_company_core.persistence import SQLiteStore


class MockCompletions:
    async def create(self, **kwargs: object) -> SimpleNamespace:
        del kwargs
        payload = {
            "action": "respond",
            "rationale": "mocked compatible provider returned a typed decision",
            "response": "compatible adapter is connected",
        }
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))],
            usage=SimpleNamespace(prompt_tokens=12, completion_tokens=9, total_tokens=21),
        )


class MockOpenAIClient:
    chat = SimpleNamespace(completions=MockCompletions())


async def main(live: bool = False) -> None:
    model_name = os.environ.get("OPENAI_MODEL", "gpt-5.6-terra")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if live:
        if not os.environ.get("OPENAI_API_KEY") and not base_url:
            raise SystemExit("--live requires OPENAI_API_KEY or OPENAI_BASE_URL")
        model = OpenAICompatibleModel(model=model_name, base_url=base_url)
    else:
        model = OpenAICompatibleModel(
            model=model_name,
            base_url=base_url or "http://127.0.0.1:8000/v1",
            client=MockOpenAIClient(),
        )

    with TemporaryDirectory(prefix="agent-company-openai-") as temporary:
        engine = MissionEngine(
            store=SQLiteStore(Path(temporary) / "state.sqlite3"),
            providers={"fast": model, "reasoning": model, "vision": model},
        )
        mission = engine.create_mission(
            MissionCreate(title="Compatible mission", objective="Return a harmless typed decision")
        )
        result = await engine.run_mission(mission.id)
        print("live" if live else "mocked", result.status.value, result.summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    arguments = parser.parse_args()
    asyncio.run(main(arguments.live))
