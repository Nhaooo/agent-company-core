from pathlib import Path

import pytest

from agent_company_core.skills import RestrictedRunner, SkillManifest, SkillValidationError


def test_skill_execution_is_disabled_by_default(tmp_path: Path) -> None:
    entrypoint = tmp_path / "safe.py"
    entrypoint.write_text("print('ok')\n", encoding="utf-8")
    runner = RestrictedRunner(root=tmp_path)
    with pytest.raises(SkillValidationError, match="disabled"):
        import asyncio

        asyncio.run(
            runner.run(
                SkillManifest(id="safe_skill", version="0.1.0", entrypoint="safe.py", trusted=True)
            )
        )


def test_skill_entrypoint_cannot_escape_root(tmp_path: Path) -> None:
    runner = RestrictedRunner(root=tmp_path)
    manifest = SkillManifest(
        id="safe_skill", version="0.1.0", entrypoint="../outside.py", trusted=True
    )
    with pytest.raises(SkillValidationError, match="existing file"):
        runner.validate(manifest)
