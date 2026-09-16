# Architecture

The repository is organized around narrow seams:

```text
contracts -> persistence -> orchestration
                 ^             |
models/providers ----------------+
permissions/tools/runtime/memory/observability
```

`MissionEngine` composes the seams but does not own a provider SDK. A provider
implements `ModelProvider.complete(ModelRequest) -> ModelResponse`; a store
persists mission contracts; policy decides whether a structured effect is
allowed; tools perform only registered effects; audit records the result after
recursive redaction.

## Adding a provider

1. Implement the neutral async protocol in `src/agent_company_core/integrations/`.
2. Keep the SDK optional and import it lazily.
3. Normalize configuration, timeout, transport, and malformed-response errors.
4. Validate `response_schema` and never put credentials in exceptions or logs.
5. Add injected-client tests for success, structured output, errors, timeout,
   missing configuration, fallback, and STOP.
6. Add a focused provider guide and a mocked example.

## Adding storage or integrations

Keep host-specific dependencies behind an explicit extra and document what the
adapter does not guarantee. Add conformance tests before changing the engine.
Do not make a provider or server mandatory for the offline quickstart.
