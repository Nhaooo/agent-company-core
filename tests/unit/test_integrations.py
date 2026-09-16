from types import SimpleNamespace

import pytest

from agent_company_core import AgentDecision, DecisionAction
from agent_company_core.integrations.google import GoogleModel
from agent_company_core.models import ModelRequest


class FakeGoogleModels:
    async def generate_content(self, **kwargs):
        return SimpleNamespace(
            text="ok",
            parsed={"action": "respond", "rationale": "adapter test", "response": "ok"},
        )


class FakeGoogleClient:
    def __init__(self):
        self.aio = SimpleNamespace(models=FakeGoogleModels())


@pytest.mark.asyncio
async def test_google_adapter_uses_provider_protocol_without_sdk_or_credentials() -> None:
    model = GoogleModel(model="test-model", client=FakeGoogleClient())
    response = await model.complete(ModelRequest(prompt="hello", response_schema=AgentDecision))
    assert response.provider == "google"
    assert response.structured.action is DecisionAction.RESPOND
