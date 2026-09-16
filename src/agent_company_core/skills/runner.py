"""Experimental restricted local runner; not a hostile-code sandbox."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from pathlib import Path

from pydantic import Field

from agent_company_core.contracts.common import StrictModel


class SkillManifest(StrictModel):
    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{1,63}$")
    version: str = Field(pattern=r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
    entrypoint: str
    permissions: frozenset[str] = frozenset()
    trusted: bool = False


class SkillValidationError(ValueError):
    pass


class RestrictedRunner:
    """Run a declared executable only when explicitly enabled and trusted."""

    def __init__(
        self,
        *,
        root: str | Path,
        allow_execution: bool = False,
        allowed_programs: set[str] | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.allow_execution = allow_execution
        self.allowed_programs = allowed_programs or {"python", "python.exe"}

    def validate(self, manifest: SkillManifest) -> Path:
        if not manifest.trusted:
            raise SkillValidationError("skill is not trusted")
        entrypoint = (self.root / manifest.entrypoint).resolve()
        if self.root not in entrypoint.parents or not entrypoint.is_file():
            raise SkillValidationError("entrypoint must be an existing file below the runner root")
        return entrypoint

    async def run(
        self, manifest: SkillManifest, args: Sequence[str] = (), *, timeout: float = 10.0
    ) -> tuple[int, str, str]:
        if not self.allow_execution:
            raise SkillValidationError("local skill execution is disabled by default")
        entrypoint = self.validate(manifest)
        program = "python.exe" if "python.exe" in self.allowed_programs else "python"
        process = await asyncio.create_subprocess_exec(
            program,
            str(entrypoint),
            *args,
            cwd=self.root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except TimeoutError:
            process.kill()
            await process.wait()
            raise SkillValidationError("skill execution timed out") from None
        returncode = process.returncode if process.returncode is not None else -1
        return returncode, stdout.decode(errors="replace"), stderr.decode(errors="replace")
