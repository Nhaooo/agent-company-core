"""Optional Anthropic Claude adapter.

The Anthropic SDK is imported only when an application constructs the adapter
without injecting a client. This keeps the core package and offline tests
credential-free.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import os
from typing import Any

from agent_company_core.models import (
    ModelProviderError,
    ModelRequest,
    ModelResponse,
    ProviderConfigurationError,
    ProviderTimeoutError,
    is_provider_timeout,
    parse_structured_response,
    structured_prompt,
)

from ._common import anthropic_text, usage_values


class AnthropicModel:
    """Implement :class:`ModelProvider` using Anthropic's Messages API.

    ``model`` is deliberately required so model lifecycle changes cannot be
    hidden behind a stale adapter default. The SDK reads the standard
    ``ANTHROPIC_API_KEY`` environment variable when no explicit key is given.
    """

    name = "anthropic"

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        max_tokens: int = 1024,
        timeout: float | None = 60.0,
        client: Any | None = None,
    ) -> None:
        if not model.strip():
            raise ValueError("model must not be empty")
        if max_tokens < 1:
            raise ValueError("max_tokens must be positive")
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout
        if client is None:
            configured_key = api_key if api_key is not None else os.environ.get("ANTHROPIC_API_KEY")
            if not configured_key:
                raise ProviderConfigurationError("ANTHROPIC_API_KEY is not configured")
            try:
                sdk = importlib.import_module("anthropic")
            except ImportError as exc:
                raise ProviderConfigurationError(
                    "install agent-company-core[anthropic] to use AnthropicModel"
                ) from exc
            options: dict[str, Any] = {"api_key": configured_key}
            if timeout is not None:
                options["timeout"] = timeout
            client = sdk.AsyncAnthropic(**options)
        self.client = client

    async def complete(self, request: ModelRequest) -> ModelResponse:
        parameters: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": structured_prompt(request)}],
        }
        if request.system:
            parameters["system"] = request.system
        try:
            response = self.client.messages.create(**parameters)
            if inspect.isawaitable(response):
                response = await response
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if is_provider_timeout(exc):
                raise ProviderTimeoutError("Anthropic request timed out") from exc
            raise ModelProviderError(
                f"Anthropic request failed: {type(exc).__name__}"
            ) from exc

        text = anthropic_text(response)
        structured = parse_structured_response(
            text, request.response_schema, provider=self.name
        )
        usage = usage_values(getattr(response, "usage", None), ("input_tokens", "output_tokens"))
        return ModelResponse(
            text=text,
            model=self.model,
            provider=self.name,
            structured=structured,
            usage=usage,
            raw=response,
        )
