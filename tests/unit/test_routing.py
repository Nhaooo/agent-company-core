from agent_company_core import RoutingAssessment, select_model_route
from agent_company_core.models import Modality, RoutePurpose


def test_route_uses_structured_assessment() -> None:
    route = select_model_route(
        RoutingAssessment(
            complexity=0.9, ambiguity=0.2, risk=0.8, continuity=0.7, purpose=RoutePurpose.REASONING
        ),
        fallbacks={"reasoning": ("fast",)},
    )
    assert route.candidates == ("reasoning", "fast")
    assert "elevated risk" in route.rationale


def test_vision_route_is_not_text_keyword_routing() -> None:
    route = select_model_route(
        RoutingAssessment(
            complexity=0.1, ambiguity=0.1, risk=0.1, continuity=0.1, modality=Modality.VISION
        )
    )
    assert route.primary == "vision"
