"""agent-company-core public API."""

from .agents import AgentRegistry, AgentSpec, demo_registry
from .contracts import (
    AgentDecision,
    DecisionAction,
    Mission,
    MissionCreate,
    MissionResult,
    MissionStatus,
    RiskLevel,
)
from .models import (
    FakeEmbedding,
    FakeModel,
    ModelProvider,
    ModelRequest,
    ModelResponse,
    RoutingAssessment,
    select_model_route,
)
from .orchestration import MissionEngine
from .permissions import ActionRequest, ApprovalRequest, ApprovalResolution, Policy, PolicyDecision
from .runtime import StopControl, StopRequested

__version__ = "0.1.0"

__all__ = [
    "ActionRequest",
    "AgentDecision",
    "AgentRegistry",
    "AgentSpec",
    "ApprovalRequest",
    "ApprovalResolution",
    "DecisionAction",
    "FakeEmbedding",
    "FakeModel",
    "Mission",
    "MissionCreate",
    "MissionEngine",
    "MissionResult",
    "MissionStatus",
    "ModelProvider",
    "ModelRequest",
    "ModelResponse",
    "Policy",
    "PolicyDecision",
    "RiskLevel",
    "RoutingAssessment",
    "StopControl",
    "StopRequested",
    "demo_registry",
    "select_model_route",
]
