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
from .integrations import AnthropicModel, OpenAICompatibleModel
from .models import (
    ConfigurationCheck,
    FakeEmbedding,
    FakeModel,
    ModelProvider,
    ModelProviderError,
    ModelRequest,
    ModelResponse,
    ProviderConfigurationError,
    ProviderResponseError,
    ProviderTimeoutError,
    RoutingAssessment,
    check_base_url,
    check_model,
    check_runtime_directory,
    provider_configuration_checks,
    select_model_route,
)
from .orchestration import MissionEngine
from .permissions import ActionRequest, ApprovalRequest, ApprovalResolution, Policy, PolicyDecision
from .runtime import StopControl, StopRequested

__version__ = "0.2.0"

__all__ = [
    "ActionRequest",
    "AnthropicModel",
    "AgentDecision",
    "AgentRegistry",
    "AgentSpec",
    "ApprovalRequest",
    "ApprovalResolution",
    "ConfigurationCheck",
    "DecisionAction",
    "FakeEmbedding",
    "FakeModel",
    "Mission",
    "MissionCreate",
    "MissionEngine",
    "MissionResult",
    "MissionStatus",
    "ModelProviderError",
    "ModelProvider",
    "ModelRequest",
    "ModelResponse",
    "OpenAICompatibleModel",
    "Policy",
    "PolicyDecision",
    "ProviderConfigurationError",
    "ProviderResponseError",
    "ProviderTimeoutError",
    "RiskLevel",
    "RoutingAssessment",
    "StopControl",
    "StopRequested",
    "check_base_url",
    "check_model",
    "check_runtime_directory",
    "demo_registry",
    "provider_configuration_checks",
    "select_model_route",
]