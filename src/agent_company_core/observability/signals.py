"""Provider-neutral observability contracts and privacy policy."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import AbstractContextManager, contextmanager
from typing import Protocol, TypeAlias

AttributeValue: TypeAlias = str | bool | int | float

SPAN_NAMES = frozenset(
    {
        "agent_company.mission.run",
        "agent_company.provider.call",
        "agent_company.approval.resolve",
        "agent_company.tool.execute",
        "agent_company.checkpoint.save",
    }
)

METRIC_NAMES = frozenset(
    {
        "agent_company.lifecycle.events",
        "agent_company.operation.duration",
        "agent_company.operation.failures",
    }
)

ATTRIBUTE_ALLOWLIST = frozenset(
    {
        "mission.id",
        "agent.id",
        "provider.name",
        "provider.model",
        "provider.route",
        "tool.name",
        "approval.id",
        "approval.approved",
        "mission.status",
        "operation.name",
        "event.name",
        "error.type",
    }
)


def allowlisted_attributes(
    attributes: Mapping[str, object] | None,
) -> dict[str, AttributeValue]:
    """Return scalar attributes explicitly approved for telemetry export."""

    if not attributes:
        return {}
    return {
        key: value
        for key, value in attributes.items()
        if key in ATTRIBUTE_ALLOWLIST and isinstance(value, str | bool | int | float)
    }


class Observability(Protocol):
    """Small provider-neutral surface consumed by the orchestration core."""

    def operation(
        self, name: str, attributes: Mapping[str, object] | None = None
    ) -> AbstractContextManager[None]: ...

    def record_event(
        self, name: str, attributes: Mapping[str, object] | None = None
    ) -> None: ...


class NoOpObservability:
    """Default observer; keeps OpenTelemetry fully optional."""

    @contextmanager
    def operation(
        self, name: str, attributes: Mapping[str, object] | None = None
    ) -> Iterator[None]:
        del name, attributes
        yield

    def record_event(
        self, name: str, attributes: Mapping[str, object] | None = None
    ) -> None:
        del name, attributes
