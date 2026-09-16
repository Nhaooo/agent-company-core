"""Neutral agent definitions and capability-based delegation."""

from dataclasses import dataclass, field

from agent_company_core.contracts import RiskLevel

_RISK_ORDER = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2, RiskLevel.CRITICAL: 3}


@dataclass(frozen=True, slots=True)
class AgentSpec:
    id: str
    role: str
    capabilities: frozenset[str] = field(default_factory=frozenset)
    max_risk: RiskLevel = RiskLevel.MEDIUM
    description: str = ""


class AgentRegistry:
    """Registry that selects agents by declared capability and risk ceiling."""

    def __init__(self, agents: list[AgentSpec] | None = None) -> None:
        self._agents: dict[str, AgentSpec] = {}
        for agent in agents or []:
            self.register(agent)

    def register(self, agent: AgentSpec) -> None:
        if not agent.id or not agent.id.replace("_", "").isalnum():
            raise ValueError("agent ids must be simple identifiers")
        if agent.id in self._agents:
            raise ValueError(f"agent already registered: {agent.id}")
        self._agents[agent.id] = agent

    def get(self, agent_id: str) -> AgentSpec:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise KeyError(f"unknown agent: {agent_id}") from exc

    def all(self) -> tuple[AgentSpec, ...]:
        return tuple(self._agents.values())

    def select(
        self,
        *,
        capabilities: set[str] | frozenset[str] = frozenset(),
        risk: RiskLevel = RiskLevel.LOW,
    ) -> AgentSpec:
        eligible = [
            agent
            for agent in self._agents.values()
            if _RISK_ORDER[agent.max_risk] >= _RISK_ORDER[risk]
        ]
        if not eligible:
            raise LookupError(f"no agent is allowed to handle risk={risk.value}")
        return max(
            eligible,
            key=lambda agent: (len(capabilities & agent.capabilities), -len(agent.id), agent.id),
        )

    def select_many(
        self, *, capabilities: set[str], risk: RiskLevel = RiskLevel.LOW, limit: int = 3
    ) -> tuple[AgentSpec, ...]:
        if limit < 1:
            raise ValueError("limit must be positive")
        eligible = [
            agent
            for agent in self._agents.values()
            if _RISK_ORDER[agent.max_risk] >= _RISK_ORDER[risk]
        ]
        return tuple(
            sorted(eligible, key=lambda agent: (-len(capabilities & agent.capabilities), agent.id))[
                :limit
            ]
        )


def demo_registry() -> AgentRegistry:
    """Return neutral agents used by examples, not a fixed private roster."""

    return AgentRegistry(
        [
            AgentSpec(
                "planner",
                "Planner",
                frozenset({"planning", "decomposition"}),
                RiskLevel.HIGH,
                "Breaks objectives into verifiable steps.",
            ),
            AgentSpec(
                "researcher",
                "Researcher",
                frozenset({"research", "evidence"}),
                RiskLevel.MEDIUM,
                "Collects evidence through registered tools.",
            ),
            AgentSpec(
                "reviewer",
                "Reviewer",
                frozenset({"review", "verification"}),
                RiskLevel.HIGH,
                "Checks outputs against explicit acceptance criteria.",
            ),
        ]
    )
