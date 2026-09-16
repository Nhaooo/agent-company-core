"""Optional Temporal integration boundary.

The core engine remains usable without a Temporal server. This adapter is a
small gateway for applications that want to start an externally defined
workflow; workflow code belongs in the host application so it can preserve
its own deterministic workflow constraints.
"""

from typing import Any


async def connect_temporal(target: str, *, namespace: str = "default") -> Any:
    try:
        from temporalio.client import Client  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("install agent-company-core[temporal] to use Temporal") from exc
    return await Client.connect(target, namespace=namespace)
