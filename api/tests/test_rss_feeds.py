"""Unit tests for RSS feed API endpoints."""
import sqlite3
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from api.database import init_db
from api.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    init_db(database_url=db_path)

    import api.database as db_module
    import api.services.rss_feed_service as rss_module
    import api.services.settings_service as settings_module

    def fake_get(url, timeout=5.0, follow_redirects=True):
        class Response:
            status_code = 200
            text = "<?xml version='1.0'?><rss><channel><title>Example</title></channel></rss>"

        return Response()

    def fake_post(url, json, timeout=5.0):
        class Response:
            status_code = 204

        return Response()

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
    monkeypatch.setattr(rss_module, "get_db", patched_get_db)
    monkeypatch.setattr(settings_module, "get_db", patched_get_db)
    monkeypatch.setattr(rss_module.httpx, "get", fake_get)
    monkeypatch.setattr(rss_module.httpx, "post", fake_post)
    monkeypatch.setattr(settings_module.httpx, "post", fake_post)

    with TestClient(app) as c:
        yield c


def create_feed(client, url="https://example.com/feed.xml", title="Example"):
    return client.post("/rss-feeds", json={"url": url, "title": title})


def test_create_rss_feed_returns_201(client):
    resp = create_feed(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["url"] == "https://example.com/feed.xml"
    assert body["title"] == "Example"
    assert "id" in body


def test_set_rss_webhook_accepts_discord_webhook_url(client):
    resp = client.put(
        "/settings/webhook",
        json={"webhook_url": "https://discord.com/api/webhooks/1/token"},
    )
    assert resp.status_code == 200
    assert resp.json()["webhook_url"] == "https://discord.com/api/webhooks/1/token"


def test_ping_webhook_returns_200(client):
    resp = client.post(
        "/settings/webhook/ping",
        json={"webhook_url": "https://discord.com/api/webhooks/1/token"},
    )
    assert resp.status_code == 200
    assert resp.json()["pong"] is True


def test_list_rss_feeds_returns_200(client):
    create_feed(client, url="https://a.example.com/feed", title="A")
    create_feed(client, url="https://b.example.com/feed", title="B")
    resp = client.get("/rss-feeds")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_get_rss_feed_returns_200(client):
    feed_id = create_feed(client).json()["id"]
    resp = client.get(f"/rss-feeds/{feed_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == feed_id


def test_update_rss_feed_returns_200(client):
    feed_id = create_feed(client, title="Old").json()["id"]
    resp = client.patch(f"/rss-feeds/{feed_id}", json={"title": "New"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"


def test_execute_rss_feed_returns_200(client):
    client.put(
        "/settings/webhook",
        json={"webhook_url": "https://discord.com/api/webhooks/1/token"},
    )
    feed_id = client.post(
        "/rss-feeds",
        json={"url": "https://example.com/feed.xml", "title": "Example"},
    ).json()["id"]
    resp = client.post(f"/rss-feeds/{feed_id}/execute")
    assert resp.status_code == 200
    assert resp.json()["feed_id"] == feed_id
    assert resp.json()["delivered"] is True


def test_execute_rss_feed_without_webhook_returns_400(client):
    feed_id = create_feed(client).json()["id"]
    resp = client.post(f"/rss-feeds/{feed_id}/execute")
    assert resp.status_code == 400


def test_delete_rss_feed_returns_204(client):
    feed_id = create_feed(client).json()["id"]
    resp = client.delete(f"/rss-feeds/{feed_id}")
    assert resp.status_code == 204


def test_create_rss_feed_with_duplicate_url_returns_409(client):
    create_feed(client)
    resp = create_feed(client)
    assert resp.status_code == 409


def test_create_rss_feed_with_invalid_url_returns_422(client):
    resp = client.post("/rss-feeds", json={"url": "not-a-url", "title": "Test"})
    assert resp.status_code == 422


def test_create_rss_feed_with_non_discord_webhook_returns_422(client):
    resp = client.put("/settings/webhook", json={"webhook_url": "https://example.com/webhook"})
    assert resp.status_code == 422


def test_ping_webhook_with_non_discord_url_returns_422(client):
    resp = client.post("/settings/webhook/ping", json={"webhook_url": "https://example.com/webhook"})
    assert resp.status_code == 422


def test_get_rss_webhook_returns_404_when_unconfigured(client):
    resp = client.get("/settings/webhook")
    assert resp.status_code == 404


def test_create_rss_feed_with_empty_title_returns_422(client):
    resp = client.post("/rss-feeds", json={"url": "https://example.com/feed", "title": "   "})
    assert resp.status_code == 422


def test_create_rss_feed_with_non_feed_url_returns_422(client, monkeypatch):
    import api.services.rss_feed_service as rss_module

    def fake_get(url, timeout=5.0, follow_redirects=True):
        class Response:
            status_code = 200
            text = "<html><body>Not a feed</body></html>"

        return Response()

    monkeypatch.setattr(rss_module.httpx, "get", fake_get)

    resp = create_feed(client, url="https://example.com/not-a-feed.xml")
    assert resp.status_code == 422


def test_get_nonexistent_rss_feed_returns_404(client):
    resp = client.get("/rss-feeds/99999")
    assert resp.status_code == 404
