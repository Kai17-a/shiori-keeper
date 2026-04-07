"""Unit tests for Folder API endpoints (Requirements 5.1, 5.2, 5.3, 5.5, 5.6)."""
import pytest
from fastapi.testclient import TestClient

from api.app.main import app
from api.app.database import init_db, get_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    """TestClient with an isolated in-memory DB for each test."""
    db_path = str(tmp_path / "test.db")
    init_db(database_url=db_path)

    # Patch get_db to use the temp DB
    import api.app.database as db_module
    import api.app.services.folder_service as fs_module
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
    monkeypatch.setattr(fs_module, "get_db", patched_get_db)

    with TestClient(app) as c:
        yield c


# --- Happy path ---

def test_create_folder_returns_201(client):
    response = client.post("/folders", json={"name": "Work"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Work"
    assert "id" in data
    assert "created_at" in data


def test_list_folders_returns_200(client):
    client.post("/folders", json={"name": "A"})
    client.post("/folders", json={"name": "B"})
    response = client.get("/folders")
    assert response.status_code == 200
    names = [f["name"] for f in response.json()]
    assert "A" in names
    assert "B" in names


def test_delete_folder_returns_204(client):
    create_resp = client.post("/folders", json={"name": "ToDelete"})
    folder_id = create_resp.json()["id"]
    response = client.delete(f"/folders/{folder_id}")
    assert response.status_code == 204


def test_deleted_folder_not_in_list(client):
    create_resp = client.post("/folders", json={"name": "Gone"})
    folder_id = create_resp.json()["id"]
    client.delete(f"/folders/{folder_id}")
    names = [f["name"] for f in client.get("/folders").json()]
    assert "Gone" not in names


# --- Error cases ---

def test_create_folder_without_name_returns_422(client):
    response = client.post("/folders", json={})
    assert response.status_code == 422


def test_delete_nonexistent_folder_returns_404(client):
    response = client.delete("/folders/99999")
    assert response.status_code == 404
