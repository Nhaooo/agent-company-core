"""Small helpers shared by optional model adapters."""

from collections.abc import Mapping, Sequence
from typing import Any


def block_text(block: Any) -> str:
    value = block.get("text") if isinstance(block, Mapping) else getattr(block, "text", None)
    return value if isinstance(value, str) else ""


def anthropic_text(response: Any) -> str:
    content = getattr(response, "content", None)
    if isinstance(content, Sequence) and not isinstance(content, str | bytes | bytearray):
        return "".join(block_text(block) for block in content)
    value = getattr(response, "text", "")
    return value if isinstance(value, str) else ""


def openai_text(response: Any) -> str:
    choices = getattr(response, "choices", None)
    if not isinstance(choices, Sequence) or not choices:
        return ""
    choice = choices[0]
    message = (
        choice.get("message")
        if isinstance(choice, Mapping)
        else getattr(choice, "message", None)
    )
    if isinstance(message, Mapping):
        value = message.get("content")
    else:
        value = getattr(message, "content", None)
    return value if isinstance(value, str) else ""


def usage_values(value: Any, names: Sequence[str]) -> dict[str, int]:
    usage: dict[str, int] = {}
    for name in names:
        item = value.get(name) if isinstance(value, Mapping) else getattr(value, name, None)
        if isinstance(item, int):
            usage[name] = item
    return usage
