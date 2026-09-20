from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from uuid import UUID

import pytest
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from agent_company_core import AgentDecision, DecisionAction, MissionCreate, RiskLevel
from agent_company_core.models import ModelRequest, ModelResponse
from agent_company_core.observability import (
    ATTRIBUTE_ALLOWLIST,
    OpenTelemetryObservability,
    allowlisted_attributes,
)
from agent_company_core.orchestration import MissionEngine
from agent_company_core.permissions import ApprovalResolution
from agent_company_core.persistence import SQLiteStore
from agent_company_core.tools import ToolRegistry, ToolSpec


class DecisionProvider:
    name = "test-provider"

    def __init__(self, decision: AgentDecision) -> None:
        self.decision = decision

    async def complete(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            text="",
            model="test-model",
            provider=self.name,
            structured=self.decision,
        )


def observer() -> tuple[
    OpenTelemetryObservability,
    InMemorySpanExporter,
    InMemoryMetricReader,
]:
    exporter = InMemorySpanExporter()
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))
    reader = InMemoryMetricReader()
    meter_provider = MeterProvider(metric_readers=[reader])
    return (
        OpenTelemetryObservability(
            tracer_provider=tracer_provider,
            meter_provider=meter_provider,
        ),
        exporter,
        reader,
    )


def metric_names(reader: InMemoryMetricReader) -> set[str]:
    data = reader.get_metrics_data()
    return {
        metric.name
        for resource in data.resource_metrics
        for scope in resource.scope_metrics
        for metric in scope.metrics
    }


def exported_attributes(spans: Iterable[object]) -> list[dict[str, object]]:
    values: list[dict[str, object]] = []
    for span in spans:
        values.append(dict(span.attributes))  # type: ignore[attr-defined]
        values.extend(dict(event.attributes) for event in span.events)  # type: ignore[attr-defined]
    return values


def test_allowlist_drops_content_credentials_and_unknown_fields() -> None:
    safe = allowlisted_attributes(
        {
            "mission.id": "mission-1",
            "provider.name": "local",
            "prompt": "private prompt",
            "response": "private response",
            "tool.arguments": "secret argument",
            "user.email": "person@example.com",
            "api_key": "sk-private",
            "mission.status": ["not", "scalar"],
        }
    )

    assert safe == {"mission.id": "mission-1", "provider.name": "local"}
    assert set(safe) <= ATTRIBUTE_ALLOWLIST


def test_in_memory_exporter_contains_only_allowlisted_metadata() -> None:
    telemetry, exporter, reader = observer()

    with telemetry.operation(
        "agent_company.provider.call",
        {
            "mission.id": "mission-1",
            "provider.route": "fast",
            "prompt": "do not export me",
            "authorization": "Bearer private-token",
        },
    ):
        telemetry.record_event(
            "model.completed",
            {
                "provider.name": "synthetic",
                "provider.model": "test-model",
                "response": "also private",
            },
        )
    with pytest.raises(RuntimeError, match="sensitive failure detail"), telemetry.operation(
        "agent_company.provider.call",
        {"mission.id": "mission-1", "provider.route": "fallback"},
    ):
        raise RuntimeError("sensitive failure detail")

    spans = exporter.get_finished_spans()
    assert [span.name for span in spans] == [
        "agent_company.provider.call",
        "agent_company.provider.call",
    ]
    attributes = exported_attributes(spans)
    assert all(set(item) <= ATTRIBUTE_ALLOWLIST for item in attributes)
    serialized = repr(spans)
    assert "do not export me" not in serialized
    assert "private-token" not in serialized
    assert "also private" not in serialized
    assert "sensitive failure detail" not in serialized
    assert any(item.get("error.type") == "RuntimeError" for item in attributes)
    assert metric_names(reader) == {
        "agent_company.lifecycle.events",
        "agent_company.operation.duration",
        "agent_company.operation.failures",
    }


@pytest.mark.asyncio
async def test_engine_correlates_approval_tool_checkpoint_and_stop_without_payloads(
    tmp_path: Path,
) -> None:
    telemetry, exporter, reader = observer()
    tools = ToolRegistry()
    tools.register(
        ToolSpec(
            "deploy",
            "controlled test effect",
            frozenset({"release"}),
            lambda arguments: {"target": arguments["target"]},
            risk=RiskLevel.HIGH,
        )
    )
    decision = AgentDecision(
        action=DecisionAction.USE_TOOL,
        rationale="requires approval",
        tool_name="deploy",
        tool_arguments={"target": "secret-target"},
    )
    provider = DecisionProvider(decision)
    engine = MissionEngine(
        store=SQLiteStore(tmp_path / "state.sqlite3"),
        providers={"fast": provider, "reasoning": provider},
        tools=tools,
        observability=telemetry,
    )
    mission = engine.create_mission(
        MissionCreate(title="Private", objective="customer secret objective")
    )

    waiting = await engine.run_mission(mission.id)
    row = engine.store.list_approvals(mission.id)[0]
    approval_id = UUID(row["id"])
    engine.resolve_approval(
        approval_id,
        ApprovalResolution(
            approved=True,
            resolved_by="operator@example.com",
            request_hash=row["request_hash"],
        ),
    )
    await engine.execute_approved(approval_id)
    engine.checkpoint(mission.id, "private checkpoint content")

    stopped = engine.create_mission(
        MissionCreate(title="Stopped", objective="another secret objective")
    )
    engine.request_stop("private operator reason")
    stopped_result = await engine.run_mission(stopped.id)

    assert waiting.status.value == "waiting_approval"
    assert stopped_result.status.value == "stopped"
    spans = exporter.get_finished_spans()
    span_names = {span.name for span in spans}
    assert {
        "agent_company.mission.run",
        "agent_company.provider.call",
        "agent_company.approval.resolve",
        "agent_company.tool.execute",
        "agent_company.checkpoint.save",
    } <= span_names
    event_names = {event.name for span in spans for event in span.events}
    assert {
        "approval.requested",
        "approval.resolved",
        "approved_effect.executed",
        "mission.checkpointed",
        "mission.stopped",
    } <= event_names
    attributes = exported_attributes(spans)
    assert all(set(item) <= ATTRIBUTE_ALLOWLIST for item in attributes)
    serialized = repr(spans)
    for sensitive in (
        "customer secret objective",
        "secret-target",
        "operator@example.com",
        "private checkpoint content",
        "private operator reason",
    ):
        assert sensitive not in serialized
    assert metric_names(reader) == {
        "agent_company.lifecycle.events",
        "agent_company.operation.duration",
    }
