import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from agent_company_core import (
    AgentDecision,
    AnthropicModel,
    DecisionAction,
    MissionCreate,
    MissionEngine,
    OpenAICompatibleModel,
    ProviderConfigurationError,
    ProviderTimeoutError,
)
from agent_company_core.models import FakeModel, ModelRequest
from agent_company_core.persistence import SQLiteStore


def _decision_json() -> str:
    return json.dumps(
        {
            "action": "respond",
            "rationale": "structured provider response",
            "response": "done",
        }
    )


class AnthropicMessages:
    def __init__(self, response: object | None = None, error: Exception | None = None) -> None:
        self.response = response or SimpleNamespace(
            content=[SimpleNamespace(text=_decision_json())],
            usage=SimpleNamespace(input_tokens=4, output_tokens=5),
        )
        self.error = error
        self.calls: list[dict[str, object]] = []

    async def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


class AnthropicClient:
    def __init__(self, messages: AnthropicMessages) -> None:
        self.messages = messages


class OpenAICompletions:
    def __init__(self, response: object | None = None, error: Exception | None = None) -> None:
        self.response = response or SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=_decision_json()))],
            usage=SimpleNamespace(prompt_tokens=4, completion_tokens=5, total_tokens=9),
        )
        self.error = error
        self.calls: list[dict[str, object]] = []

    async def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


class OpenAIChat:
    def __init__(self, completions: OpenAICompletions) -> None:
        self.completions = completions


class OpenAIClient:
    def __init__(self, completions: OpenAICompletions) -> None:
        self.chat = OpenAIChat(completions)


class APITimeoutError(Exception):
    pass


@pytest.mark.asyncio
async def test_anthropic_adapter_validates_structured_output() -> None:
    messages = AnthropicMessages()
    provider = AnthropicModel(model="claude-sonnet-4-6", client=AnthropicClient(messages))

    response = await provider.complete(
        ModelRequest(prompt="Return a decision", system="Be precise", response_schema=AgentDecision)
    )

    assert response.provider == "anthropic"
    assert response.model == "claude-sonnet-4-6"
    assert isinstance(response.structured, AgentDecision)
    assert response.structured.action is DecisionAction.RESPOND
    assert messages.calls[0]["system"] == "Be precise"
    assert "Return only one JSON object" in str(messages.calls[0]["messages"])


@pytest.mark.asyncio
async def test_openai_compatible_adapter_validates_structured_output() -> None:
    completions = OpenAICompletions()
    provider = OpenAICompatibleModel(
        model="local-test-model",
        base_url="http://127.0.0.1:11434/v1",
        client=OpenAIClient(completions),
    )

    response = await provider.complete(
        ModelRequest(prompt="Return a decision", response_schema=AgentDecision)
    )

    assert response.provider == "openai-compatible"
    assert isinstance(response.structured, AgentDecision)
    assert completions.calls[0]["response_format"] == {"type": "json_object"}


def test_provider_configuration_does_not_need_an_optional_sdk_for_missing_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)

    with pytest.raises(ProviderConfigurationError, match="ANTHROPIC_API_KEY"):
        AnthropicModel(model="claude-sonnet-4-6")
    with pytest.raises(ProviderConfigurationError, match="OPENAI_API_KEY"):
        OpenAICompatibleModel(model="model")


@pytest.mark.asyncio
async def test_timeout_is_normalized_without_provider_message() -> None:
    anthropic = AnthropicModel(
        model="claude-sonnet-4-6",
        client=AnthropicClient(
            AnthropicMessages(error=APITimeoutError("secret-looking provider details"))
        ),
    )
    with pytest.raises(ProviderTimeoutError) as error:
        await anthropic.complete(ModelRequest(prompt="timeout"))
    assert "secret-looking" not in str(error.value)

    openai = OpenAICompatibleModel(
        model="model",
        client=OpenAIClient(OpenAICompletions(error=APITimeoutError("private details"))),
    )
    with pytest.raises(ProviderTimeoutError) as error:
        await openai.complete(ModelRequest(prompt="timeout"))
    assert "private details" not in str(error.value)


@pytest.mark.asyncio
async def test_anthropic_error_falls_back_and_never_logs_error_text(tmp_path: Path) -> None:
    provider = AnthropicModel(
        model="claude-sonnet-4-6",
        client=AnthropicClient(
            AnthropicMessages(error=RuntimeError("do-not-log-this-provider-detail"))
        ),
    )
    fallback = FakeModel("fallback completed")
    engine = MissionEngine(
        store=SQLiteStore(tmp_path / "state.sqlite3"),
        providers={"fast": provider, "reasoning": fallback},
    )
    mission = engine.create_mission(MissionCreate(title="Fallback", objective="Use fallback"))

    result = await engine.run_mission(mission.id)

    assert result.status.value == "completed"
    audit = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "model.failed" in audit
    assert "do-not-log-this-provider-detail" not in audit


@pytest.mark.asyncio
async def test_stop_prevents_anthropic_request(tmp_path: Path) -> None:
    messages = AnthropicMessages()
    engine = MissionEngine(
        store=SQLiteStore(tmp_path / "state.sqlite3"),
        providers={
            "fast": AnthropicModel(model="claude-sonnet-4-6", client=AnthropicClient(messages)),
        },
    )
    mission = engine.create_mission(
        MissionCreate(title="Stopped", objective="Do not call provider")
    )
    engine.request_stop("operator stop")

    result = await engine.run_mission(mission.id)

    assert result.status.value == "stopped"
    assert messages.calls == []
