"""Use the Anthropic adapter with a mocked client unless --live is explicit."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from agent_company_core import AnthropicModel, MissionCreate, MissionEngine
from agent_company_core.persistence import SQLiteStore


class MockMessages:
    async def create(self, **kwargs: object) -> SimpleNamespace:
        del kwargs
        payload = {
            "action": "respond",
            "rationale": "mocked Claude returned a typed decision",
            "response": "Claude adapter is connected",
        }
        return SimpleNamespace(
            content=[SimpleNamespace(text=json.dumps(payload))],
            usage=SimpleNamespace(input_tokens=12, output_tokens=9),
        )


class MockAnthropicClient:
    messages = MockMessages()


async def main(live: bool = False) -> None:
    model_name = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    if live:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("--live requires ANTHROPIC_API_KEY; default mode is offline")
        model = AnthropicModel(model=model_name)
    else:
        model = AnthropicModel(model=model_name, client=MockAnthropicClient())

    with TemporaryDirectory(prefix="agent-company-anthropic-") as temporary:
        engine = MissionEngine(
            store=SQLiteStore(Path(temporary) / "state.sqlite3"),
            providers={"fast": model, "reasoning": model, "vision": model},
        )
        mission = engine.create_mission(
            MissionCreate(title="Claude mission", objective="Return a harmless typed decision")
        )
        result = await engine.run_mission(mission.id)
        print("live" if live else "mocked", result.status.value, result.summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    arguments = parser.parse_args()
    asyncio.run(main(arguments.live))
