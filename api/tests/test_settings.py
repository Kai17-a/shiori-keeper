"""Unit tests for Settings API endpoints."""

import sqlite3
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.tests.test_support import build_test_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test.db")
    build_test_db(db_path)

    import api.database as db_module
    import api.services.settings_service as settings_module

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
    monkeypatch.setattr(settings_module, "get_db", patched_get_db)

    with TestClient(app) as c:
        yield c


def test_get_webhook_returns_404_when_unconfigured(client):
    resp = client.get("/settings/webhook")
    assert resp.status_code == 404


def test_set_and_get_webhook_round_trip(client):
    webhook_url = "https://discord.com/api/webhooks/1/token"
    put_resp = client.put("/settings/webhook", json={"webhook_url": webhook_url})
    assert put_resp.status_code == 200
    assert put_resp.json()["webhook_url"] == webhook_url

    get_resp = client.get("/settings/webhook")
    assert get_resp.status_code == 200
    assert get_resp.json()["webhook_url"] == webhook_url


def test_set_webhook_accepts_teams_webhook_url(client):
    webhook_url = "https://contoso.webhook.office.com/webhookb2/abc/IncomingWebhook/def/ghi"
    resp = client.put("/settings/webhook", json={"webhook_url": webhook_url})
    assert resp.status_code == 200
    assert resp.json()["webhook_url"] == webhook_url


def test_set_webhook_rejects_discord_host_with_wrong_path(client):
    resp = client.put(
        "/settings/webhook",
        json={"webhook_url": "https://discord.com/channels/1/2"},
    )
    assert resp.status_code == 422
    assert resp.json()["detail"] == "Webhook URL must be a Discord or Microsoft Teams webhook URL"


def test_ping_webhook_maps_httpx_error_to_502(client, monkeypatch):
    import httpx
    import api.services.webhook_service as webhook_module

    def fake_post(url, json, timeout=5.0):
        raise httpx.ConnectError("boom")

    monkeypatch.setattr(webhook_module.httpx, "post", fake_post)

    resp = client.post(
        "/settings/webhook/ping",
        json={"webhook_url": "https://discord.com/api/webhooks/1/token"},
    )
    assert resp.status_code == 502
    assert resp.json()["detail"] == "Failed to reach Discord webhook"


def test_rss_execution_setting_can_toggle_true_and_false(client):
    first = client.get("/settings/rss-execution")
    assert first.status_code == 200
    assert first.json()["enabled"] is False

    enabled = client.put("/settings/rss-execution", json={"enabled": True})
    assert enabled.status_code == 200
    assert enabled.json()["enabled"] is True

    disabled = client.put("/settings/rss-execution", json={"enabled": False})
    assert disabled.status_code == 200
    assert disabled.json()["enabled"] is False

    last = client.get("/settings/rss-execution")
    assert last.status_code == 200
    assert last.json()["enabled"] is False
