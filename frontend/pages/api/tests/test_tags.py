"""Unit tests for Tag API endpoints (Requirements 6.1, 6.2, 6.3, 6.5, 6.6)."""
import pytest
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.database import init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    """TestClient with an isolated temp DB for each test."""
    db_path = str(tmp_path / "test.db")
    init_db(database_url=db_path)

    import api.app.database as db_module
    import api.app.services.tag_service as ts_module
    from contextlib import contextmanager
    import sqlite3

    @contextmanager
    def patched_get_db(database_url=db_path):
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    monkeypatch.setattr(db_module, "get_db", patched_get_db)
    monkeypatch.setattr(ts_module, "get_db", patched_get_db)

    with TestClient(app) as c:
        yield c


# --- Happy path ---

def test_create_tag_returns_201(client):
    response = client.post("/tags", json={"name": "python"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "python"
    assert "id" in data


def test_list_tags_returns_200(client):
    client.post("/tags", json={"name": "alpha"})
    client.post("/tags", json={"name": "beta"})
    response = client.get("/tags")
    assert response.status_code == 200
    names = [t["name"] for t in response.json()]
    assert "alpha" in names
    assert "beta" in names


def test_delete_tag_returns_204(client):
    create_resp = client.post("/tags", json={"name": "removeme"})
    tag_id = create_resp.json()["id"]
    response = client.delete(f"/tags/{tag_id}")
    assert response.status_code == 204


def test_deleted_tag_not_in_list(client):
    create_resp = client.post("/tags", json={"name": "gone"})
    tag_id = create_resp.json()["id"]
    client.delete(f"/tags/{tag_id}")
    names = [t["name"] for t in client.get("/tags").json()]
    assert "gone" not in names


# --- Error cases ---

def test_create_duplicate_tag_returns_409(client):
    client.post("/tags", json={"name": "unique"})
    response = client.post("/tags", json={"name": "unique"})
    assert response.status_code == 409


def test_delete_nonexistent_tag_returns_404(client):
    response = client.delete("/tags/99999")
    assert response.status_code == 404
