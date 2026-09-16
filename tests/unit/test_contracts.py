import pytest
from pydantic import ValidationError

from agent_company_core import AgentDecision, DecisionAction, MissionCreate


def test_contracts_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        MissionCreate(title="x", objective="y", unexpected=True)  # type: ignore[call-arg]


def test_decision_is_typed_and_serializable() -> None:
    decision = AgentDecision(action=DecisionAction.RESPOND, rationale="done", response="ok")
    assert decision.model_dump(mode="json")["action"] == "respond"
