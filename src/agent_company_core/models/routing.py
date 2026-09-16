"""Structured model routing with no message-keyword business rules."""

from dataclasses import dataclass
from enum import StrEnum

from pydantic import Field

from agent_company_core.contracts.common import StrictModel


class Modality(StrEnum):
    TEXT = "text"
    VISION = "vision"


class RoutePurpose(StrEnum):
    SIMPLE = "simple"
    REASONING = "reasoning"
    VISION = "vision"


class RoutingAssessment(StrictModel):
    complexity: float = Field(ge=0, le=1)
    ambiguity: float = Field(ge=0, le=1)
    risk: float = Field(ge=0, le=1)
    continuity: float = Field(ge=0, le=1)
    modality: Modality = Modality.TEXT
    purpose: RoutePurpose = RoutePurpose.SIMPLE


@dataclass(frozen=True, slots=True)
class ModelRoute:
    primary: str
    fallbacks: tuple[str, ...]
    rationale: tuple[str, ...]

    @property
    def candidates(self) -> tuple[str, ...]:
        return (self.primary, *self.fallbacks)


def select_model_route(
    assessment: RoutingAssessment,
    *,
    simple: str = "fast",
    reasoning: str = "reasoning",
    vision: str = "vision",
    fallbacks: dict[str, tuple[str, ...]] | None = None,
) -> ModelRoute:
    """Select from declared capabilities using typed assessment fields."""

    if assessment.modality is Modality.VISION:
        primary = vision
        rationale = ["vision modality"]
    elif assessment.purpose is RoutePurpose.REASONING or assessment.complexity >= 0.55:
        primary = reasoning
        rationale = ["reasoning purpose or high complexity"]
    else:
        primary = simple
        rationale = ["routine complexity"]
    if assessment.risk >= 0.7:
        rationale.append("elevated risk")
    if assessment.continuity >= 0.6:
        rationale.append("continuity-sensitive request")
    fallback_map = fallbacks or {}
    return ModelRoute(primary, tuple(fallback_map.get(primary, ())), tuple(rationale))
