from pathlib import Path

import pytest


def test_reference_app_exposes_real_health_chat_and_persistence(tmp_path: Path) -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from agent_company_core.reference.app import create_app

    client = TestClient(create_app(tmp_path))
    assert client.get("/health").json() == {"status": "ok", "provider": "fake"}
    response = client.post("/chat", json={"message": "a harmless request"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert client.post("/memory", json={"content": "remember this durable note"}).status_code == 200
    assert client.get("/memory/search", params={"q": "durable"}).json()
