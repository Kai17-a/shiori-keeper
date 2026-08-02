"""Tests for LLM-assisted custom news-site scraping."""

import logging
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
    import api.services.news_site_service as news_module
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

    html = """
    <html><body><main class="news-list">
      <article class="news-item">
        <h2><a href="/articles/first">First article</a></h2>
        <time datetime="2026-08-01T10:00:00+09:00">August 1</time>
        <p class="summary">First summary</p>
      </article>
      <article class="news-item">
        <h2><a href="https://example.com/articles/second">Second article</a></h2>
        <time datetime="2026-08-02T10:00:00+09:00">August 2</time>
      </article>
    </main></body></html>
    """

    class PageResponse:
        status_code = 200
        text = html

    scrape_config = {
        "site_title": "Example News",
        "item_selector": ".news-item",
        "title_selector": "h2 a",
        "link_selector": "h2 a",
        "link_attribute": "href",
        "published_selector": "time",
        "published_attribute": "datetime",
        "summary_selector": ".summary",
    }

    monkeypatch.setattr(db_module, "get_db", patched_get_db)
    monkeypatch.setattr(news_module, "get_db", patched_get_db)
    monkeypatch.setattr(settings_module, "get_db", patched_get_db)
    monkeypatch.setattr(news_module.httpx, "get", lambda *args, **kwargs: PageResponse())
    monkeypatch.setattr(
        news_module,
        "analyze_news_page",
        lambda _config, *, page_url, html, reference_id: scrape_config,
    )
    monkeypatch.setattr(settings_module, "test_llm_connection", lambda _config: "pong")

    with TestClient(app) as test_client:
        yield test_client


def configure_llm(client):
    return client.put(
        "/settings/llm",
        json={
            "provider": "ollama",
            "base_url": "http://127.0.0.1:11434",
            "model": "llama3.2",
        },
    )


def create_site(client, **overrides):
    body = {"url": "https://example.com/news", **overrides}
    return client.post("/news-sites", json=body)


def test_registration_requires_llm_settings(client):
    response = create_site(client)

    assert response.status_code == 400
    assert "LLM settings" in response.json()["detail"]


def test_registration_analyzes_and_tests_scraping_before_saving(client):
    assert configure_llm(client).status_code == 200

    response = create_site(client, description="Custom source")

    assert response.status_code == 201
    assert response.json()["title"] == "Example News"
    assert response.json()["description"] == "Custom source"
    assert response.json()["webhook_ids"] == []
    listed = client.get("/news-sites")
    assert listed.json()["total"] == 1


def test_registration_rejects_a_recipe_that_extracts_no_articles(
    client, monkeypatch, caplog
):
    import api.services.news_site_service as news_module

    configure_llm(client)
    monkeypatch.setattr(
        news_module,
        "analyze_news_page",
        lambda _config, *, page_url, html, reference_id: {
            "site_title": "Broken",
            "item_selector": ".missing",
            "title_selector": "a",
            "link_selector": "a",
            "link_attribute": "href",
            "published_selector": None,
            "published_attribute": None,
            "summary_selector": None,
        },
    )

    with caplog.at_level(logging.ERROR):
        response = create_site(client)

    assert response.status_code == 422
    assert response.json()["detail"].startswith("Selector extraction error:")
    assert "LLM request succeeded" in response.json()["detail"]
    assert "Reference ID:" in response.json()["detail"]
    assert "news_extraction_empty" in caplog.text
    assert client.get("/news-sites").json()["total"] == 0


def test_registration_requires_extracted_titles(client, monkeypatch):
    import api.services.news_site_service as news_module

    configure_llm(client)
    monkeypatch.setattr(
        news_module,
        "analyze_news_page",
        lambda _config, *, page_url, html, reference_id: {
            "site_title": "Broken",
            "item_selector": ".news-item",
            "title_selector": ".missing-title",
            "link_selector": "a",
            "link_attribute": "href",
            "published_selector": None,
            "published_attribute": None,
            "summary_selector": None,
        },
    )

    response = create_site(client)

    assert response.status_code == 422
    assert response.json()["detail"].startswith("Selector extraction error:")
    assert client.get("/news-sites").json()["total"] == 0


def test_registration_identifies_target_site_automation_block(
    client, monkeypatch, caplog
):
    import api.services.news_site_service as news_module

    class ForbiddenResponse:
        status_code = 403
        text = "<html><title>Forbidden</title></html>"
        headers = {"server": "cloudflare"}

    configure_llm(client)
    monkeypatch.setattr(
        news_module.httpx, "get", lambda *args, **kwargs: ForbiddenResponse()
    )

    with caplog.at_level(logging.ERROR):
        response = create_site(client)

    assert response.status_code == 422
    assert response.json()["detail"].startswith("Target-site fetch error:")
    assert "HTTP 403 before LLM analysis" in response.json()["detail"]
    assert "block automated requests" in response.json()["detail"]
    assert "Reference ID:" in response.json()["detail"]
    assert "news_site_fetch_rejected" in caplog.text
    assert "cloudflare" in caplog.text
    assert "Forbidden" in caplog.text


def test_manual_execution_notifies_and_records_only_new_articles(client, monkeypatch):
    import api.services.news_site_service as news_module

    configure_llm(client)
    webhook = client.post(
        "/settings/webhooks",
        json={
            "name": "Discord alerts",
            "webhook_url": "https://discord.com/api/webhooks/1/token",
        },
    )
    site = create_site(client, webhook_ids=[webhook.json()["id"]])
    payloads = []

    class WebhookResponse:
        status_code = 204

    monkeypatch.setattr(
        news_module,
        "send_webhook",
        lambda url, payload: payloads.append((url, payload)) or WebhookResponse(),
    )

    first = client.post(f"/news-sites/{site.json()['id']}/execute")
    second = client.post(f"/news-sites/{site.json()['id']}/execute")
    articles = client.get(f"/news-sites/{site.json()['id']}/articles")

    assert first.status_code == 200
    assert first.json()["message"] == "Posted 2 new article(s)."
    assert second.json()["message"] == "No new articles found."
    assert len(payloads) == 1
    assert articles.json()["total"] == 2
    assert articles.json()["items"][0]["title"] == "Second article"


def test_duplicate_news_site_url_is_rejected_before_registration(client):
    configure_llm(client)
    assert create_site(client).status_code == 201

    duplicate = create_site(client)

    assert duplicate.status_code == 409
