"""Optional Google Gen AI adapter.

Importing this module does not require the optional dependency; constructing
the adapter does and produces a clear installation error when absent.
"""

from __future__ import annotations

from typing import Any

from agent_company_core.models import ModelRequest, ModelResponse


class GoogleModel:
    name = "google"

    def __init__(
        self,
        *,
        model: str,
        project: str | None = None,
        location: str | None = None,
        client: Any | None = None,
    ) -> None:
        if client is None:
            try:
                from google import genai
            except ImportError as exc:
                raise RuntimeError("install agent-company-core[google] to use GoogleModel") from exc
            client = genai.Client(vertexai=bool(project), project=project, location=location)
        self.model = model
        self.client = client

    async def complete(self, request: ModelRequest) -> ModelResponse:
        config: Any = {}
        if request.response_schema is not None:
            config["response_mime_type"] = "application/json"
            config["response_schema"] = request.response_schema
        prompt = f"{request.system}\n\n{request.prompt}" if request.system else request.prompt
        response = await self.client.aio.models.generate_content(
            model=self.model, contents=prompt, config=config or None
        )
        structured = None
        if request.response_schema is not None and getattr(response, "parsed", None) is not None:
            structured = request.response_schema.model_validate(response.parsed)
        text = getattr(response, "text", "") or ""
        return ModelResponse(
            text=text, model=self.model, provider=self.name, structured=structured, raw=response
        )
