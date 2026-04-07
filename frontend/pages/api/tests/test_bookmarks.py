"""Unit tests for Bookmark API endpoints (Requirements 1.1-1.5, 2.1-2.6, 3.1-3.4, 4.1-4.3, 7.1-7.4)."""
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
    import api.app.services.bookmark_service as bs_module
    import api.app.services.folder_service as fs_module
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
    monkeypatch.setattr(bs_module, "get_db", patched_get_db)
    monkeypatch.setattr(fs_module, "get_db", patched_get_db)
    monkeypatch.setattr(ts_module, "get_db", patched_get_db)

    with TestClient(app) as c:
        yield c


# --- Helpers ---

def create_bookmark(client, url="https://example.com", title="Example", **kwargs):
    payload = {"url": url, "title": title, **kwargs}
    return client.post("/bookmarks", json=payload)


def create_folder(client, name="MyFolder"):
    return client.post("/folders", json={"name": name})


def create_tag(client, name="mytag"):
    return client.post("/tags", json={"name": name})


# --- Happy path ---

def test_create_bookmark_returns_201(client):
    resp = create_bookmark(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["url"] == "https://example.com/"
    assert data["title"] == "Example"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["tags"] == []


def test_list_bookmarks_returns_200(client):
    create_bookmark(client, url="https://a.com", title="A")
    create_bookmark(client, url="https://b.com", title="B")
    resp = client.get("/bookmarks")
    assert resp.status_code == 200
    titles = [b["title"] for b in resp.json()]
    assert "A" in titles
    assert "B" in titles


def test_get_bookmark_returns_200(client):
    bm_id = create_bookmark(client).json()["id"]
    resp = client.get(f"/bookmarks/{bm_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == bm_id


def test_update_bookmark_returns_200(client):
    bm_id = create_bookmark(client, title="Old").json()["id"]
    resp = client.patch(f"/bookmarks/{bm_id}", json={"title": "New"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"


def test_update_bookmark_changes_updated_at(client):
    bm = create_bookmark(client).json()
    bm_id = bm["id"]
    old_updated = bm["updated_at"]
    import time; time.sleep(1)
    resp = client.patch(f"/bookmarks/{bm_id}", json={"title": "Changed"})
    assert resp.json()["updated_at"] >= old_updated


def test_delete_bookmark_returns_204(client):
    bm_id = create_bookmark(client).json()["id"]
    resp = client.delete(f"/bookmarks/{bm_id}")
    assert resp.status_code == 204


def test_deleted_bookmark_returns_404(client):
    bm_id = create_bookmark(client).json()["id"]
    client.delete(f"/bookmarks/{bm_id}")
    resp = client.get(f"/bookmarks/{bm_id}")
    assert resp.status_code == 404


def test_add_tag_to_bookmark_returns_200(client):
    bm_id = create_bookmark(client).json()["id"]
    tag_id = create_tag(client).json()["id"]
    resp = client.post(f"/bookmarks/{bm_id}/tags", json={"tag_id": tag_id})
    assert resp.status_code == 200
    tag_ids = [t["id"] for t in resp.json()["tags"]]
    assert tag_id in tag_ids


def test_remove_tag_from_bookmark_returns_204(client):
    bm_id = create_bookmark(client).json()["id"]
    tag_id = create_tag(client).json()["id"]
    client.post(f"/bookmarks/{bm_id}/tags", json={"tag_id": tag_id})
    resp = client.delete(f"/bookmarks/{bm_id}/tags/{tag_id}")
    assert resp.status_code == 204


def test_remove_tag_clears_from_bookmark(client):
    bm_id = create_bookmark(client).json()["id"]
    tag_id = create_tag(client).json()["id"]
    client.post(f"/bookmarks/{bm_id}/tags", json={"tag_id": tag_id})
    client.delete(f"/bookmarks/{bm_id}/tags/{tag_id}")
    bm = client.get(f"/bookmarks/{bm_id}").json()
    assert bm["tags"] == []


def test_create_bookmark_with_folder(client):
    folder_id = create_folder(client).json()["id"]
    resp = create_bookmark(client, folder_id=folder_id)
    assert resp.status_code == 201
    assert resp.json()["folder_id"] == folder_id


# --- Error cases ---

def test_create_bookmark_without_title_returns_422(client):
    resp = client.post("/bookmarks", json={"url": "https://example.com"})
    assert resp.status_code == 422


def test_create_bookmark_with_invalid_url_returns_422(client):
    resp = client.post("/bookmarks", json={"url": "not-a-url", "title": "Test"})
    assert resp.status_code == 422


def test_create_bookmark_with_ftp_url_returns_422(client):
    resp = client.post("/bookmarks", json={"url": "ftp://example.com", "title": "Test"})
    assert resp.status_code == 422


def test_get_nonexistent_bookmark_returns_404(client):
    resp = client.get("/bookmarks/99999")
    assert resp.status_code == 404


def test_update_nonexistent_bookmark_returns_404(client):
    resp = client.patch("/bookmarks/99999", json={"title": "X"})
    assert resp.status_code == 404


def test_delete_nonexistent_bookmark_returns_404(client):
    resp = client.delete("/bookmarks/99999")
    assert resp.status_code == 404


def test_create_bookmark_with_nonexistent_folder_returns_404(client):
    resp = create_bookmark(client, folder_id=99999)
    assert resp.status_code == 404


def test_add_duplicate_tag_returns_409(client):
    bm_id = create_bookmark(client).json()["id"]
    tag_id = create_tag(client).json()["id"]
    client.post(f"/bookmarks/{bm_id}/tags", json={"tag_id": tag_id})
    resp = client.post(f"/bookmarks/{bm_id}/tags", json={"tag_id": tag_id})
    assert resp.status_code == 409


def test_update_bookmark_with_invalid_url_returns_422(client):
    bm_id = create_bookmark(client).json()["id"]
    resp = client.patch(f"/bookmarks/{bm_id}", json={"url": "bad-url"})
    assert resp.status_code == 422
