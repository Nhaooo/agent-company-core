import pytest

from agent_company_core import RiskLevel, demo_registry
from agent_company_core.permissions import ActionRequest, Policy
from agent_company_core.runtime import StopControl
from agent_company_core.tools import ToolRegistry, ToolSpec


def test_agent_selection_is_capability_based() -> None:
    assert demo_registry().select(capabilities={"research"}).id == "researcher"


@pytest.mark.asyncio
async def test_low_risk_tool_executes_and_high_risk_requires_approval(tmp_path) -> None:
    registry = ToolRegistry()
    registry.register(
        ToolSpec("echo", "echo", frozenset({"text"}), lambda args: {"value": args["value"]})
    )
    result = await registry.execute(
        "echo", {"value": "ok"}, policy=Policy(), stop=StopControl(tmp_path / "stop.json")
    )
    assert result.output == {"value": "ok"}
    assert (
        Policy()
        .evaluate(ActionRequest(action="deploy", target="service", risk=RiskLevel.HIGH))
        .requires_approval
    )
