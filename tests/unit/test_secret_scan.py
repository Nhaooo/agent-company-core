from pathlib import Path

from scripts.secret_scan import scan


def test_secret_scan_has_no_findings_in_public_tree() -> None:
    root = Path(__file__).resolve().parents[2]
    assert scan(root) == []
