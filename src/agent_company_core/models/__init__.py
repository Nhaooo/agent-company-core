"""Provider-neutral model interfaces."""

from .base import (
    EmbeddingProvider,
    FakeEmbedding,
    FakeModel,
    ModelProvider,
    ModelRequest,
    ModelResponse,
)
from .routing import Modality, ModelRoute, RoutePurpose, RoutingAssessment, select_model_route

__all__ = [
    "EmbeddingProvider",
    "FakeEmbedding",
    "FakeModel",
    "ModelProvider",
    "ModelRequest",
    "ModelResponse",
    "ModelRoute",
    "Modality",
    "RoutePurpose",
    "RoutingAssessment",
    "select_model_route",
]
