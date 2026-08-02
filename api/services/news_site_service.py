from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

from api.database import get_db
from api.model.models import (
    NewsSiteArticleListResponse,
    NewsSiteArticleResponse,
    NewsSiteCreate,
    NewsSiteExecuteResponse,
    NewsSiteListResponse,
    NewsSiteResponse,
    NewsSiteUpdate,
)
from api.repositories.news_site_repo import NewsSiteRepository
from api.repositories.settings_repo import SettingsRepository
from api.repositories.webhook_endpoint_repo import WebhookEndpointRepository
from api.services.llm_service import analyze_news_page, load_llm_config
from api.services.webhook_service import (
    build_rss_notification_payload,
    detect_webhook_service,
    send_webhook,
)

logger = logging.getLogger(__name__)

MAX_ARTICLES_PER_RUN = 100


def _read_element_value(element, selector: object, attribute: object) -> str | None:
    if not isinstance(selector, str) or not selector:
        return None
    selected = element.select_one(selector)
    if selected is None:
        return None
    if isinstance(attribute, str) and attribute:
        value = selected.get(attribute)
        return str(value).strip() if value is not None else None
    value = selected.get_text(" ", strip=True)
    return value or None


def _normalize_published(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value.strip()
    normalized = candidate.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).isoformat(sep=" ")
    except ValueError:
        try:
            return parsedate_to_datetime(candidate).isoformat(sep=" ")
        except (TypeError, ValueError, OverflowError):
            return None


def extract_news_articles(
    *, html: str, page_url: str, scrape_config: dict[str, object]
) -> list[dict[str, object]]:
    """Extract normalized articles from HTML using a validated LLM recipe."""
    soup = BeautifulSoup(html, "html.parser")
    try:
        items = soup.select(str(scrape_config["item_selector"]))
    except Exception as exc:
        raise HTTPException(
            status_code=422, detail="The generated scraping configuration is invalid"
        ) from exc

    articles: list[dict[str, object]] = []
    seen_urls: set[str] = set()
    for item in items:
        try:
            title = _read_element_value(
                item, str(scrape_config["title_selector"]), None
            )
            link = _read_element_value(
                item,
                str(scrape_config["link_selector"]),
                str(scrape_config["link_attribute"]),
            )
            published = _read_element_value(
                item,
                scrape_config.get("published_selector"),
                scrape_config.get("published_attribute"),
            )
            summary = _read_element_value(
                item, scrape_config.get("summary_selector"), None
            )
        except Exception as exc:
            raise HTTPException(
                status_code=422, detail="The generated scraping configuration is invalid"
            ) from exc

        if not title or not link:
            continue
        article_url = urljoin(page_url, link)
        parsed = urlparse(article_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        if article_url in seen_urls:
            continue
        seen_urls.add(article_url)
        articles.append(
            {
                "url": article_url,
                "title": title,
                "summary": summary,
                "published": _normalize_published(published),
            }
        )
        if len(articles) >= MAX_ARTICLES_PER_RUN:
            break
    return articles


class NewsSiteService:
    def _fetch_page(self, url: str) -> str:
        try:
            response = httpx.get(url, timeout=15.0, follow_redirects=True)
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=422, detail="News site URL is not reachable"
            ) from exc
        if response.status_code >= 400:
            raise HTTPException(status_code=422, detail="News site URL is not reachable")
        if not response.text.strip():
            raise HTTPException(status_code=422, detail="News site returned empty HTML")
        return response.text

    def _analyze_and_test(self, url: str) -> tuple[dict[str, object], list[dict[str, object]]]:
        with get_db() as conn:
            llm_config = load_llm_config(SettingsRepository(conn))
        if llm_config is None:
            raise HTTPException(
                status_code=400,
                detail="LLM settings must be configured before registering a news site",
            )
        html = self._fetch_page(url)
        scrape_config = analyze_news_page(llm_config, page_url=url, html=html)
        articles = extract_news_articles(
            html=html, page_url=url, scrape_config=scrape_config
        )
        if not articles:
            raise HTTPException(
                status_code=422,
                detail="No news articles could be extracted from the site",
            )
        return scrape_config, articles

    def _verify_webhooks(self, conn, webhook_ids: list[int]) -> None:
        repo = WebhookEndpointRepository(conn)
        if any(repo.find_by_id(webhook_id) is None for webhook_id in webhook_ids):
            raise HTTPException(status_code=404, detail="Webhook endpoint not found")

    def _sync_webhooks(
        self, repo: NewsSiteRepository, site_id: int, webhook_ids: list[int] | None
    ) -> None:
        if webhook_ids is None:
            return
        self._verify_webhooks(repo.conn, webhook_ids)
        repo.set_webhook_ids(site_id, webhook_ids)

    def _to_response(self, row: dict) -> NewsSiteResponse:
        response_row = {key: value for key, value in row.items() if key != "scrape_config"}
        return NewsSiteResponse(**response_row)

    def create(self, data: NewsSiteCreate) -> NewsSiteResponse:
        url = str(data.url)
        with get_db() as conn:
            repo = NewsSiteRepository(conn)
            if repo.find_by_url(url) is not None:
                raise HTTPException(status_code=409, detail="News site URL already exists")
            if data.webhook_ids is not None:
                self._verify_webhooks(conn, data.webhook_ids)

        scrape_config, _ = self._analyze_and_test(url)
        title = data.title or str(scrape_config["site_title"])
        with get_db() as conn:
            repo = NewsSiteRepository(conn)
            try:
                row = repo.insert(
                    url=url,
                    title=title,
                    description=data.description,
                    scrape_config=json.dumps(scrape_config, ensure_ascii=False),
                )
            except sqlite3.IntegrityError as exc:
                raise HTTPException(
                    status_code=409, detail="News site URL already exists"
                ) from exc
            self._sync_webhooks(repo, int(row["id"]), data.webhook_ids)
            saved = repo.find_by_id(int(row["id"]))
            assert saved is not None
            return self._to_response(saved)

    def list(
        self, *, q: str | None = None, page: int = 1, per_page: int = 20
    ) -> NewsSiteListResponse:
        with get_db() as conn:
            repo = NewsSiteRepository(conn)
            total = repo.count_all(q)
            total_pages = (total + per_page - 1) // per_page if total else 0
            if total_pages and page > total_pages:
                page = total_pages
            rows = repo.find_all(q, per_page, (page - 1) * per_page)
            return NewsSiteListResponse(
                items=[self._to_response(row) for row in rows],
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
            )

    def get(self, site_id: int) -> NewsSiteResponse:
        with get_db() as conn:
            row = NewsSiteRepository(conn).find_by_id(site_id)
            if row is None:
                raise HTTPException(status_code=404, detail="News site not found")
            return self._to_response(row)

    def update(self, site_id: int, data: NewsSiteUpdate) -> NewsSiteResponse:
        with get_db() as conn:
            repo = NewsSiteRepository(conn)
            current = repo.find_by_id(site_id)
            if current is None:
                raise HTTPException(status_code=404, detail="News site not found")

        payload = data.model_dump(exclude_unset=True)
        fields: dict[str, object] = {}
        if "url" in payload:
            url = str(payload["url"])
            if url != current["url"]:
                with get_db() as conn:
                    existing = NewsSiteRepository(conn).find_by_url(url)
                if existing is not None and int(existing["id"]) != site_id:
                    raise HTTPException(
                        status_code=409, detail="News site URL already exists"
                    )
                scrape_config, _ = self._analyze_and_test(url)
                fields["url"] = url
                fields["scrape_config"] = json.dumps(
                    scrape_config, ensure_ascii=False
                )
        if "title" in payload:
            fields["title"] = payload["title"]
        if "description" in payload:
            fields["description"] = payload["description"]
        if "notify_webhook_enabled" in payload:
            fields["notify_webhook_enabled"] = int(payload["notify_webhook_enabled"])

        with get_db() as conn:
            repo = NewsSiteRepository(conn)
            if "webhook_ids" in payload:
                self._sync_webhooks(repo, site_id, payload["webhook_ids"])
            try:
                row = repo.update(site_id, fields)
            except sqlite3.IntegrityError as exc:
                raise HTTPException(
                    status_code=409, detail="News site URL already exists"
                ) from exc
            assert row is not None
            return self._to_response(row)

    def delete(self, site_id: int) -> None:
        with get_db() as conn:
            if not NewsSiteRepository(conn).delete(site_id):
                raise HTTPException(status_code=404, detail="News site not found")

    def list_articles(
        self,
        site_id: int,
        *,
        q: str | None = None,
        page: int = 1,
        per_page: int = 20,
        published_from: str | None = None,
        published_to: str | None = None,
    ) -> NewsSiteArticleListResponse:
        with get_db() as conn:
            repo = NewsSiteRepository(conn)
            if repo.find_by_id(site_id) is None:
                raise HTTPException(status_code=404, detail="News site not found")
            total = repo.count_articles(
                site_id,
                q=q,
                published_from=published_from,
                published_to=published_to,
            )
            total_pages = (total + per_page - 1) // per_page if total else 0
            if total_pages and page > total_pages:
                page = total_pages
            rows = repo.find_articles(
                site_id,
                q=q,
                published_from=published_from,
                published_to=published_to,
                limit=per_page,
                offset=(page - 1) * per_page,
            )
            return NewsSiteArticleListResponse(
                items=[NewsSiteArticleResponse(**row) for row in rows],
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
            )

    def execute(self, site_id: int) -> NewsSiteExecuteResponse:
        with get_db() as conn:
            repo = NewsSiteRepository(conn)
            row = repo.find_by_id(site_id)
            if row is None:
                raise HTTPException(status_code=404, detail="News site not found")
            webhook_rows = WebhookEndpointRepository(conn).find_all()
            selected = set(repo.find_webhook_ids(site_id))
            if selected:
                webhook_rows = [
                    webhook
                    for webhook in webhook_rows
                    if int(webhook["id"]) in selected
                ]
            if not webhook_rows:
                raise HTTPException(
                    status_code=400, detail="Webhook URL is not configured"
                )
            sent_urls = repo.load_sent_article_urls(site_id)

        html = self._fetch_page(str(row["url"]))
        try:
            scrape_config = json.loads(str(row["scrape_config"]))
        except ValueError as exc:
            raise HTTPException(
                status_code=500, detail="Stored scraping configuration is invalid"
            ) from exc
        articles = [
            article
            for article in extract_news_articles(
                html=html, page_url=str(row["url"]), scrape_config=scrape_config
            )
            if str(article["url"]) not in sent_urls
        ]
        if not articles:
            return NewsSiteExecuteResponse(
                site_id=site_id,
                title=str(row["title"]),
                delivered=True,
                delivered_count=0,
                message="No new articles found.",
            )

        chunks = [articles[index : index + 10] for index in range(0, len(articles), 10)]
        delivered_count = 0
        for webhook in webhook_rows:
            webhook_url = str(webhook["url"])
            service = detect_webhook_service(webhook_url)
            delivered = True
            try:
                for index, chunk in enumerate(chunks, start=1):
                    response = send_webhook(
                        webhook_url,
                        build_rss_notification_payload(
                            service,
                            feed_title=str(row["title"]),
                            articles=chunk,
                            total_articles=len(articles),
                            chunk_index=index,
                            chunk_count=len(chunks),
                        ),
                    )
                    if response.status_code >= 400:
                        delivered = False
                        break
            except httpx.HTTPError:
                delivered = False
            if delivered:
                delivered_count += 1

        if delivered_count == 0:
            raise HTTPException(status_code=502, detail="Failed to notify webhook")

        with get_db() as conn:
            NewsSiteRepository(conn).record_sent_articles(site_id, articles)
        return NewsSiteExecuteResponse(
            site_id=site_id,
            title=str(row["title"]),
            delivered=True,
            delivered_count=delivered_count,
            message=f"Posted {len(articles)} new article(s).",
        )
