"""Recursive redaction before audit persistence or user-facing output."""

import re
from collections.abc import Mapping, Sequence
from typing import Any

REDACTED = "[REDACTED]"
SENSITIVE_KEY = re.compile(
    r"(^|_)(secret|token|password|passwd|api_key|private_key|credential|cookie|authorization)(_|$)",
    re.I,
)
SENSITIVE_VALUE = re.compile(
    r"(-----BEGIN [A-Z ]*PRIVATE KEY-----|Bearer\s+[A-Za-z0-9._~+/=-]{12,}|AIza[0-9A-Za-z_-]{20,})",
    re.I,
)


def redact(value: Any, *, key: str | None = None) -> Any:
    if key and SENSITIVE_KEY.search(key):
        return REDACTED
    if isinstance(value, Mapping):
        return {str(k): redact(v, key=str(k)) for k, v in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return SENSITIVE_VALUE.sub(REDACTED, value)
    return value
