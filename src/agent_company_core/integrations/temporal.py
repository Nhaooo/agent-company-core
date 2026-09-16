"""Optional Temporal integration boundary.

The core engine remains usable without a Temporal server. This adapter is a
small gateway for applications that want to start an externally defined
workflow; workflow code belongs in the host application so it can preserve
its own deterministic workflow constraints.
"""

import importlib
from typing import Any


async def connect_temporal(target: str, *, namespace: str = "default") -> Any:
    try:
        client_module = importlib.import_module("temporalio.client")
        client = client_module.Client
    except ImportError as exc:
        raise RuntimeError("install agent-company-core[temporal] to use Temporal") from exc
    return await client.connect(target, namespace=namespace)
