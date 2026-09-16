"""Provider-neutral model and embedding protocols."""

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


class ModelProviderError(RuntimeError):
    """Base error for a provider failure safe to surface to callers."""


class ProviderConfigurationError(ModelProviderError):
    """The provider cannot be used with the supplied local configuration."""


class ProviderTimeoutError(ModelProviderError):
    """The provider request exceeded its configured timeout."""


class ProviderResponseError(ModelProviderError):
    """The provider returned data that could not satisfy the requested contract."""


def structured_prompt(request: "ModelRequest") -> str:
    """Add a provider-neutral JSON instruction when typed output is requested."""

    if request.response_schema is None:
        return request.prompt
    schema = request.response_schema
    schema_json = schema.model_json_schema() if hasattr(schema, "model_json_schema") else {}
    return (
        f"{request.prompt}\n\n"
        "Return only one JSON object matching this schema. Do not wrap it in Markdown.\n"
        f"{json.dumps(schema_json, sort_keys=True)}"
    )


def parse_structured_response(
    text: str, schema: type[Any] | None, *, provider: str
) -> Any | None:
    """Decode and validate a provider response without leaking response contents in errors."""

    if schema is None:
        return None
    if not hasattr(schema, "model_validate"):
        raise ProviderResponseError(f"{provider} response schema has no model_validate method")
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = candidate.removeprefix("```").removeprefix("json").removesuffix("```").strip()
    try:
        value = json.loads(candidate)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ProviderResponseError(
            f"{provider} returned invalid JSON for the requested schema"
        ) from exc
    try:
        return schema.model_validate(value)
    except Exception as exc:
        raise ProviderResponseError(
            f"{provider} returned JSON that does not match the requested schema"
        ) from exc


def is_provider_timeout(exc: BaseException) -> bool:
    """Recognize SDK timeout types without importing an optional provider SDK."""

    return isinstance(exc, TimeoutError) or "timeout" in type(exc).__name__.lower()


@dataclass(frozen=True, slots=True)
class ModelRequest:
    prompt: str
    system: str | None = None
    context: Sequence[Mapping[str, Any]] = field(default_factory=tuple)
    response_schema: type[Any] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ModelResponse:
    text: str
    model: str
    provider: str
    structured: Any | None = None
    usage: Mapping[str, int] = field(default_factory=dict)
    raw: Any | None = None


@runtime_checkable
class ModelProvider(Protocol):
    name: str

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Complete a request without performing application-side effects."""


@runtime_checkable
class EmbeddingProvider(Protocol):
    name: str

    async def embed(self, text: str) -> list[float]:
        """Return an embedding for text."""


class FakeModel:
    """Deterministic model for tests and the reference application."""

    name = "fake"

    def __init__(self, response: str = "Acknowledged.") -> None:
        self.response = response
        self.requests: list[ModelRequest] = []

    async def complete(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        structured = None
        schema = request.response_schema
        if schema is not None and hasattr(schema, "model_validate"):
            structured = schema.model_validate(
                {
                    "action": "respond",
                    "rationale": "fake model decision",
                    "response": self.response,
                }
            )
        return ModelResponse(
            text=self.response, model="fake-model", provider=self.name, structured=structured
        )


class FakeEmbedding:
    """Small deterministic embedding provider that needs no network or keys."""

    name = "fake"

    async def embed(self, text: str) -> list[float]:
        values = [0.0] * 8
        for index, char in enumerate(text.encode("utf-8")):
            values[index % len(values)] += char / 255.0
        norm = max(sum(value * value for value in values) ** 0.5, 1e-12)
        return [value / norm for value in values]
