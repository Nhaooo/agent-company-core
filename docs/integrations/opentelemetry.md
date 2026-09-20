# OpenTelemetry

OpenTelemetry support is optional and provider-neutral. Install the extra and
pass SDK providers configured by the host application:

```bash
pip install "agent-company-core[otel]"
```

```python
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider

from agent_company_core.observability import OpenTelemetryObservability
from agent_company_core.orchestration import MissionEngine
from agent_company_core.persistence import SQLiteStore

telemetry = OpenTelemetryObservability(
    tracer_provider=TracerProvider(),
    meter_provider=MeterProvider(),
)
engine = MissionEngine(store=SQLiteStore("state.sqlite3"), observability=telemetry)
```

Configure exporters, resource attributes, batching, and endpoints on those SDK
providers using the standard OpenTelemetry SDK. The core does not select or
configure a vendor. Sampling follows the tracer provider's configured sampler;
the adapter does not force recording or bypass a rejected sampling decision.

## Signal contract

The adapter emits spans for mission runs, provider calls, approval resolution,
tool execution, and checkpoint persistence. It also emits counters for
lifecycle events and operation failures, plus an operation-duration histogram.
Stable signal names are defined in `agent_company_core.observability`.

Telemetry attributes cross a strict allowlist boundary. Only identifiers,
provider/model/route names, tool names, approval outcomes, mission status,
operation/event names, and exception class names may be exported. Prompts,
responses, tool arguments/results, checkpoint values, memory, credentials,
operator identities, exception messages, and arbitrary application metadata are
discarded even when passed to the adapter. Keep exporter resource attributes
free of sensitive data as well.

The host application owns exporter authentication, transport security,
collector access, regional placement, sampling rates, and backend retention.
Treat correlation identifiers as operational metadata and set retention to the
shortest period that satisfies the application's diagnostic requirements.

When the `otel` extra is not installed, the default observer remains a no-op and
the orchestration core has no OpenTelemetry runtime dependency.
