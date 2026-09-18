"""Provider-neutral configuration checks used by the CLI doctor."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class ConfigurationCheck:
    """Result of one local configuration check."""

    name: str
    ok: bool
    message: str


def _non_empty(value: str | None) -> bool:
    return bool(value and value.strip())


def _valid_base_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def check_base_url(variable: str, value: str | None) -> ConfigurationCheck:
    """Validate a provider base URL without exposing its value."""
    if not _non_empty(value):
        return ConfigurationCheck(
            variable,
            True,
            f"{variable}: not set",
        )

    if _valid_base_url(value.strip()):
        return ConfigurationCheck(
            variable,
            True,
            f"{variable}: valid URL",
        )

    return ConfigurationCheck(
        variable,
        False,
        f"{variable}: invalid URL; set it to an http:// or https:// URL",
    )


def check_model(variable: str, value: str | None) -> ConfigurationCheck:
    """Validate a configured model identifier without exposing its value."""
    if _non_empty(value):
        return ConfigurationCheck(
            variable,
            True,
            f"{variable}: configured",
        )

    return ConfigurationCheck(
        variable,
        False,
        f"{variable}: missing; set a non-empty model identifier",
    )


def check_runtime_directory(data_dir: Path) -> ConfigurationCheck:
    """Check whether the runtime directory can be created and written."""
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        probe = data_dir / ".write-check"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError:
        return ConfigurationCheck(
            "Runtime directory",
            False,
            "Runtime directory: not writable; choose a writable directory",
        )

    return ConfigurationCheck(
        "Runtime directory",
        True,
        "Runtime directory: writable",
    )


def _provider_selected(
    env: Mapping[str, str],
    variables: tuple[str, ...],
) -> bool:
    """Return whether any configuration for a provider was explicitly supplied."""
    return any(variable in env for variable in variables)


def provider_configuration_checks(
    environ: Mapping[str, str] | None = None,
) -> list[ConfigurationCheck]:
    """Validate explicitly configured provider settings.

    Credentials are checked only for presence and are never included in
    diagnostic messages.
    """
    env = os.environ if environ is None else environ
    checks: list[ConfigurationCheck] = []

    openai_variables = (
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_MODEL",
    )
    ollama_variables = (
        "OLLAMA_API_KEY",
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL",
    )
    anthropic_variables = (
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_MODEL",
    )
    google_variables = (
        "GOOGLE_API_KEY",
        "GOOGLE_CLOUD_PROJECT",
        "GOOGLE_MODEL",
    )

    if _provider_selected(env, openai_variables):
        checks.append(check_base_url("OPENAI_BASE_URL", env.get("OPENAI_BASE_URL")))
        checks.append(check_model("OPENAI_MODEL", env.get("OPENAI_MODEL")))

    if _provider_selected(env, ollama_variables):
        checks.append(check_base_url("OLLAMA_BASE_URL", env.get("OLLAMA_BASE_URL")))
        checks.append(check_model("OLLAMA_MODEL", env.get("OLLAMA_MODEL")))

    if _provider_selected(env, anthropic_variables):
        checks.append(check_model("ANTHROPIC_MODEL", env.get("ANTHROPIC_MODEL")))

    if _provider_selected(env, google_variables):
        checks.append(check_model("GOOGLE_MODEL", env.get("GOOGLE_MODEL")))

    return checks