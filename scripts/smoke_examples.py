"""Run the default, credential-free examples as an integration smoke test."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXAMPLES = (
    "examples/basic.py",
    "examples/human_approval/main.py",
    "examples/stop_recovery/main.py",
    "examples/capability_delegation/main.py",
    "examples/custom_tool/main.py",
    "examples/custom_provider/main.py",
    "examples/anthropic_claude/main.py",
    "examples/openai_compatible/main.py",
    "examples/local_ollama/main.py",
    "examples/fastapi_integration/main.py",
    "examples/research_team/main.py",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    for relative in EXAMPLES:
        path = root / relative
        print(f"running {relative}")
        subprocess.run([sys.executable, str(path)], cwd=root, check=True)
    print(f"smoke-tested {len(EXAMPLES)} examples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
