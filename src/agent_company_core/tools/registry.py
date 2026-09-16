"""Typed tool registration and execution boundary."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from agent_company_core.contracts import RiskLevel
from agent_company_core.permissions import ActionRequest, Policy
from agent_company_core.runtime import StopControl

ToolHandler = Callable[[dict[str, object]], Awaitable[dict[str, object]] | dict[str, object]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    capabilities: frozenset[str]
    handler: ToolHandler
    risk: RiskLevel = RiskLevel.LOW
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ToolResult:
    name: str
    output: dict[str, object]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, tool: ToolSpec) -> None:
        if tool.name in self._tools:
            raise ValueError(f"tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolSpec:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"unknown tool: {name}") from exc

    def list(self) -> tuple[ToolSpec, ...]:
        return tuple(self._tools.values())

    def choose(self, *, capabilities: set[str] | frozenset[str]) -> ToolSpec:
        if not capabilities:
            raise LookupError("at least one capability is required")
        candidates = [tool for tool in self._tools.values() if capabilities & tool.capabilities]
        if not candidates:
            raise LookupError("no registered tool matches the declared capabilities")
        return max(candidates, key=lambda tool: (len(capabilities & tool.capabilities), tool.name))

    async def execute(
        self,
        name: str,
        arguments: dict[str, object],
        *,
        policy: Policy,
        stop: StopControl,
        requested_by: str = "system",
        mission_id: str | None = None,
    ) -> ToolResult:
        stop.assert_running()
        tool = self.get(name)
        decision = policy.evaluate(
            ActionRequest(
                action=tool.name,
                target=tool.name,
                arguments=arguments,
                requested_by=requested_by,
                risk=tool.risk,
                mission_id=mission_id,
            )
        )
        if not decision.allowed or decision.requires_approval:
            raise PermissionError(decision.reason or "tool execution requires approval")
        value = tool.handler(arguments)
        output = await value if inspect.isawaitable(value) else value
        stop.assert_running()
        return ToolResult(name=tool.name, output=output)
