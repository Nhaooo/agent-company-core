"""Optional OpenAI-compatible chat-completions adapter.

This adapter targets the common ``/chat/completions`` contract and accepts a
custom base URL, which also covers local servers such as Ollama's OpenAI
compatibility endpoint.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import os
from typing import Any

from agent_company_core.models import (
    ModelRequest,
    ModelResponse,
    ProviderConfigurationError,
    ProviderTimeoutError,
    is_provider_timeout,
    parse_structured_response,
    structured_prompt,
)

from ._common import openai_text, usage_values


class OpenAICompatibleModel:
    """Implement :class:`ModelProvider` with a compatible async chat client.

    ``OPENAI_API_KEY`` and ``OPENAI_BASE_URL`` are used by default. A local
    base URL may omit a key; the SDK receives a non-secret placeholder because
    many local servers ignore the authorization header.
    """

    name = "openai-compatible"

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = 60.0,
        client: Any | None = None,
    ) -> None:
        if not model.strip():
            raise ValueError("model must not be empty")
        self.model = model
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        self.timeout = timeout
        if client is None:
            configured_key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY")
            if not configured_key and not self.base_url:
                raise ProviderConfigurationError(
                    "OPENAI_API_KEY is not configured; set OPENAI_BASE_URL for a local server"
                )
            options: dict[str, Any] = {"api_key": configured_key or "local"}
            if self.base_url:
                options["base_url"] = self.base_url
            if timeout is not None:
                options["timeout"] = timeout
            try:
                sdk = importlib.import_module("openai")
            except ImportError as exc:
                raise ProviderConfigurationError(
                    "install agent-company-core[openai] to use OpenAICompatibleModel"
                ) from exc
            client = sdk.AsyncOpenAI(**options)
        self.client = client

    async def complete(self, request: ModelRequest) -> ModelResponse:
        messages: list[dict[str, str]] = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        messages.append({"role": "user", "content": structured_prompt(request)})
        parameters: dict[str, Any] = {"model": self.model, "messages": messages}
        if request.response_schema is not None:
            parameters["response_format"] = {"type": "json_object"}
        try:
            response = self.client.chat.completions.create(**parameters)
            if inspect.isawaitable(response):
                response = await response
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if is_provider_timeout(exc):
                raise ProviderTimeoutError("OpenAI-compatible request timed out") from exc
            raise RuntimeError(
                f"OpenAI-compatible request failed: {type(exc).__name__}"
            ) from exc

        text = openai_text(response)
        structured = parse_structured_response(
            text, request.response_schema, provider=self.name
        )
        usage = usage_values(
            getattr(response, "usage", None), ("prompt_tokens", "completion_tokens", "total_tokens")
        )
        return ModelResponse(
            text=text,
            model=self.model,
            provider=self.name,
            structured=structured,
            usage=usage,
            raw=response,
        )
