"""Deterministic risk and approval policy over structured action requests."""

from dataclasses import dataclass, field

from agent_company_core.contracts import RiskLevel

_RISK_ORDER = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2, RiskLevel.CRITICAL: 3}


@dataclass(frozen=True, slots=True)
class ActionRequest:
    action: str
    target: str
    arguments: dict[str, object] = field(default_factory=dict)
    requested_by: str = "system"
    risk: RiskLevel = RiskLevel.LOW
    mission_id: str | None = None
    snapshot_id: str | None = None


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    allowed: bool
    requires_approval: bool = False
    reason: str = ""
    required_scope: str | None = None


class Policy:
    """Default-deny policy for sensitive effects with explicit overrides."""

    def __init__(
        self,
        *,
        approval_risk: RiskLevel = RiskLevel.HIGH,
        allowed_actions: set[str] | None = None,
        approval_actions: set[str] | None = None,
    ) -> None:
        self.approval_risk = approval_risk
        self.allowed_actions = allowed_actions
        self.approval_actions = approval_actions or {
            "publish",
            "send_message",
            "purchase",
            "deploy",
        }

    def evaluate(self, request: ActionRequest) -> PolicyDecision:
        if not request.action or not request.target:
            return PolicyDecision(False, reason="action and target are required")
        if self.allowed_actions is not None and request.action not in self.allowed_actions:
            return PolicyDecision(False, reason="action is not registered in this policy")
        if (
            _RISK_ORDER[request.risk] >= _RISK_ORDER[self.approval_risk]
            or request.action in self.approval_actions
        ):
            return PolicyDecision(
                True,
                requires_approval=True,
                reason="explicit approval boundary",
                required_scope=request.action,
            )
        return PolicyDecision(True, reason="allowed by declared policy")
