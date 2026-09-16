"""Provider-neutral model and embedding protocols."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


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
