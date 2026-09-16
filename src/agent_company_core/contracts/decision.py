"""Model-produced decisions kept separate from orchestration effects."""

from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import Field

from .common import StrictModel


class DecisionAction(StrEnum):
    RESPOND = "respond"
    USE_TOOL = "use_tool"
    CREATE_MISSION = "create_mission"
    DELEGATE = "delegate"
    REQUEST_APPROVAL = "request_approval"
    WAIT = "wait"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentDecision(StrictModel):
    """A typed, auditable intention. It never performs an effect itself."""

    id: UUID = Field(default_factory=uuid4)
    action: DecisionAction
    rationale: str = Field(min_length=1, max_length=2_000)
    risk: RiskLevel = RiskLevel.LOW
    response: str | None = Field(default=None, max_length=20_000)
    tool_name: str | None = Field(default=None, max_length=200)
    tool_capabilities: list[str] = Field(default_factory=list, max_length=20)
    tool_arguments: dict[str, object] = Field(default_factory=dict)
    mission: dict[str, object] | None = None
    agent_ids: list[str] = Field(default_factory=list, max_length=20)
    approval_request_id: UUID | None = None
