"""Exercise the reference FastAPI app in-process."""

from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx

from agent_company_core.reference.app import create_app


async def main() -> None:
    with TemporaryDirectory(prefix="agent-company-fastapi-") as temporary:
        app = create_app(Path(temporary))
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            response.raise_for_status()
            print(response.json())


if __name__ == "__main__":
    asyncio.run(main())
