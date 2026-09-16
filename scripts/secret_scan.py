"""Dependency-free fallback secret scanner for tracked files.

It reports only a relative path and a category, never matched content.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

RULES = (
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("google-key", re.compile(r"AIza[0-9A-Za-z_-]{20,}")),
    ("bearer-token", re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{20,}")),
    (
        "credential-assignment",
        re.compile(
            r"(?i)(?:api[_-]?key|secret|token|password)\s*[=:]\s*['\"]?[A-Za-z0-9/+=_.-]{16,}"
        ),
    ),
    (
        "absolute-user-path",
        re.compile(
            r"(?i)(?<![A-Za-z])(?:[A-Za-z]:[/\\]|"
            + "/"
            + "home"
            + "/|"
            + "/"
            + "Users"
            + "/)"
            + r"[^\s\"']+"
        ),
    ),
)


def tracked_files(root: Path) -> list[Path]:
    output = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"], text=False)
    return [root / item for item in output.decode().split("\0") if item]


def scan(root: Path) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for path in tracked_files(root):
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for label, rule in RULES:
            if rule.search(content):
                findings.append((path.relative_to(root).as_posix(), label))
    return findings


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings = scan(root)
    if findings:
        for path, label in findings:
            print(f"FINDING {label}: {path}")
        return 1
    print(f"No secret-pattern findings in {len(tracked_files(root))} tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
