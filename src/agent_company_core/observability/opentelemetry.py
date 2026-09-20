"""Optional OpenTelemetry adapter with a strict data-minimization boundary."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from time import perf_counter
from typing import TYPE_CHECKING, Any

from .signals import SPAN_NAMES, allowlisted_attributes

if TYPE_CHECKING:
    from opentelemetry.metrics import MeterProvider
    from opentelemetry.trace import TracerProvider


class OpenTelemetryObservability:
    """Export allowlisted lifecycle signals through configured OTel providers."""

    def __init__(
        self,
        *,
        tracer_provider: TracerProvider | None = None,
        meter_provider: MeterProvider | None = None,
        instrumentation_name: str = "agent-company-core",
    ) -> None:
        try:
            from opentelemetry import metrics, trace
        except ImportError as exc:  # pragma: no cover - exercised without the optional extra
            raise RuntimeError(
                "OpenTelemetry support requires agent-company-core[otel]"
            ) from exc

        self._tracer: Any = trace.get_tracer(
            instrumentation_name, tracer_provider=tracer_provider
        )
        self._meter: Any = metrics.get_meter(
            instrumentation_name, meter_provider=meter_provider
        )
        self._events: Any = self._meter.create_counter(
            "agent_company.lifecycle.events",
            description="Allowlisted agent-company lifecycle events",
        )
        self._duration: Any = self._meter.create_histogram(
            "agent_company.operation.duration",
            unit="s",
            description="Duration of allowlisted orchestration operations",
        )
        self._failures: Any = self._meter.create_counter(
            "agent_company.operation.failures",
            description="Failures of allowlisted orchestration operations",
        )

    @contextmanager
    def operation(
        self, name: str, attributes: Mapping[str, object] | None = None
    ) -> Iterator[None]:
        if name not in SPAN_NAMES:
            raise ValueError(f"unsupported observability span: {name}")
        safe = allowlisted_attributes({"operation.name": name, **(attributes or {})})
        started = perf_counter()
        with self._tracer.start_as_current_span(
            name,
            attributes=safe,
            record_exception=False,
            set_status_on_exception=False,
        ) as span:
            try:
                yield
            except Exception as exc:
                error_attributes = allowlisted_attributes(
                    {**safe, "error.type": type(exc).__name__}
                )
                span.set_attribute("error.type", type(exc).__name__)
                self._failures.add(1, attributes=error_attributes)
                raise
            finally:
                self._duration.record(perf_counter() - started, attributes=safe)

    def record_event(
        self, name: str, attributes: Mapping[str, object] | None = None
    ) -> None:
        safe = allowlisted_attributes({"event.name": name, **(attributes or {})})
        self._events.add(1, attributes=safe)
        from opentelemetry import trace

        span = trace.get_current_span()
        if span.is_recording():
            span.add_event(name, attributes=safe)
