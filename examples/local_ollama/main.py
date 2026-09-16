"""Use Ollama's OpenAI-compatible endpoint, with an offline mock by default."""

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
            "rationale": "mocked local model returned a typed decision",
            "response": "local Ollama path is ready",
        }
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))],
        )


class MockOpenAIClient:
    chat = SimpleNamespace(completions=MockCompletions())


async def main(live: bool = False) -> None:
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
    model_name = os.environ.get("OLLAMA_MODEL", "llama3.2")
    api_key = os.environ.get("OLLAMA_API_KEY", "ollama")
    if live:
        model = OpenAICompatibleModel(model=model_name, base_url=base_url, api_key=api_key)
    else:
        model = OpenAICompatibleModel(
            model=model_name,
            base_url=base_url,
            api_key=api_key,
            client=MockOpenAIClient(),
        )

    with TemporaryDirectory(prefix="agent-company-ollama-") as temporary:
        engine = MissionEngine(
            store=SQLiteStore(Path(temporary) / "state.sqlite3"),
            providers={"fast": model, "reasoning": model, "vision": model},
        )
        mission = engine.create_mission(
            MissionCreate(title="Local mission", objective="Return a harmless typed decision")
        )
        result = await engine.run_mission(mission.id)
        print("live" if live else "mocked", result.status.value, result.summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    arguments = parser.parse_args()
    asyncio.run(main(arguments.live))
