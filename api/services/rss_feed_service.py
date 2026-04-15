import logging
import sqlite3
import xml.etree.ElementTree as ET

import feedparser  # type: ignore
import httpx
from fastapi import HTTPException

from api.database import get_db
from api.model.models import (
    RSSFeedCreate,
    RSSFeedExecuteResponse,
    RSSFeedListResponse,
    RSSFeedResponse,
    RSSFeedUpdate,
)
from api.repositories.rss_feed_repo import RSSFeedRepository
from api.repositories.settings_repo import SettingsRepository
from api.services.settings_service import WEBHOOK_SETTING_KEY

logger = logging.getLogger(__name__)


class RSSFeedService:
    def _extract_discord_error_detail(self, response: httpx.Response) -> str | None:
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                data = response.json()
            except ValueError:
                return None

            if isinstance(data, dict):
                for key in ("detail", "message", "error"):
                    value = data.get(key)
                    if value:
                        return str(value)
                return str(data)
            return str(data)

        try:
            text = response.text.strip()
        except Exception:
            return None

        return text or None

    def _raise_discord_webhook_error(
        self, response: httpx.Response | None = None
    ) -> None:
        if response is not None:
            response_detail = self._extract_discord_error_detail(response)
            if response_detail:
                logger.error("Discord webhook notification failed: %s", response_detail)
        raise HTTPException(status_code=502, detail="Failed to notify Discord webhook")

    def _parse_rss_feed(self, content: bytes) -> feedparser.FeedParserDict:
        parsed = feedparser.parse(content)
        if parsed.bozo:
            raise HTTPException(
                status_code=422, detail="RSS feed URL is not a valid RSS feed"
            )
        if not parsed.feed and not parsed.entries:
            raise HTTPException(
                status_code=422, detail="RSS feed URL is not a valid RSS feed"
            )
        return parsed

    def _get_feed_title(
        self, parsed_feed: feedparser.FeedParserDict, fallback_title: str
    ) -> str:
        feed_data = getattr(parsed_feed, "feed", None)
        if feed_data is None and isinstance(parsed_feed, dict):
            feed_data = parsed_feed.get("feed")
        if feed_data is None:
            return fallback_title
        if isinstance(feed_data, dict):
            return str(feed_data.get("title") or fallback_title)
        return str(getattr(feed_data, "title", None) or fallback_title)

    def _validate_rss_feed_url(self, url: str) -> None:
        try:
            response = httpx.get(url, timeout=5.0, follow_redirects=True)
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=422, detail="RSS feed URL is not reachable"
            ) from exc

        if response.status_code >= 400:
            raise HTTPException(status_code=422, detail="RSS feed URL is not reachable")

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as exc:
            raise HTTPException(
                status_code=422, detail="RSS feed URL is not a valid RSS feed"
            ) from exc

        tag = root.tag.split("}", 1)[-1].lower()
        if tag == "rss":
            channel = root.find("channel")
            if channel is None:
                raise HTTPException(
                    status_code=422, detail="RSS feed URL is not a valid RSS feed"
                )
            return
        if tag == "feed":
            return

        raise HTTPException(
            status_code=422, detail="RSS feed URL is not a valid RSS feed"
        )

    def _chunk_embeds(
        self, embeds: list[dict[str, object]], chunk_size: int = 10
    ) -> list[list[dict[str, object]]]:
        return [
            embeds[index : index + chunk_size]
            for index in range(0, len(embeds), chunk_size)
        ]

    def _load_sent_article_urls(self, conn, feed_id: int) -> set[str]:
        rows = conn.execute(
            "SELECT url FROM rss_feed_articles WHERE feed_id = ?",
            (feed_id,),
        ).fetchall()
        return {str(row["url"]) for row in rows}

    def _record_sent_articles(
        self, conn, feed_id: int, articles: list[dict[str, object]]
    ) -> None:
        for article in articles:
            conn.execute(
                """
                INSERT OR IGNORE INTO rss_feed_articles (feed_id, url, title)
                VALUES (?, ?, ?)
                """,
                (feed_id, article["url"], article.get("title")),
            )

    def create(self, data: RSSFeedCreate) -> RSSFeedResponse:
        with get_db() as conn:
            repo = RSSFeedRepository(conn)
            if repo.find_by_url(str(data.url)) is not None:
                raise HTTPException(
                    status_code=409, detail="RSS feed URL already exists"
                )
            self._validate_rss_feed_url(str(data.url))
            try:
                row = repo.insert(str(data.url), data.title, data.description)
            except sqlite3.IntegrityError:
                raise HTTPException(
                    status_code=409, detail="RSS feed URL already exists"
                )
            return RSSFeedResponse(**row)

    def list(
        self, q: str | None = None, page: int = 1, per_page: int = 20
    ) -> RSSFeedListResponse:
        with get_db() as conn:
            repo = RSSFeedRepository(conn)
            total = repo.count_all(q=q)
            total_pages = max((total + per_page - 1) // per_page, 1) if total else 0
            page = max(page, 1)
            if total_pages and page > total_pages:
                page = total_pages
            offset = (page - 1) * per_page
            rows = repo.find_all(q=q, limit=per_page, offset=offset)
            items = [RSSFeedResponse(**row) for row in rows]
            return RSSFeedListResponse(
                items=items,
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
            )

    def get(self, feed_id: int) -> RSSFeedResponse:
        with get_db() as conn:
            repo = RSSFeedRepository(conn)
            row = repo.find_by_id(feed_id)
            if row is None:
                raise HTTPException(status_code=404, detail="RSS feed not found")
            return RSSFeedResponse(**row)

    def update(self, feed_id: int, data: RSSFeedUpdate) -> RSSFeedResponse:
        with get_db() as conn:
            repo = RSSFeedRepository(conn)
            if repo.find_by_id(feed_id) is None:
                raise HTTPException(status_code=404, detail="RSS feed not found")
            fields: dict[str, object] = {}
            if data.url is not None:
                existing = repo.find_by_url(str(data.url))
                if existing is not None and existing["id"] != feed_id:
                    raise HTTPException(
                        status_code=409, detail="RSS feed URL already exists"
                    )
                self._validate_rss_feed_url(str(data.url))
                fields["url"] = str(data.url)
            if data.title is not None:
                fields["title"] = data.title
            if data.description is not None:
                fields["description"] = data.description
            row = repo.update(feed_id, fields)
            assert row is not None
            return RSSFeedResponse(**row)

    def delete(self, feed_id: int) -> None:
        with get_db() as conn:
            repo = RSSFeedRepository(conn)
            if not repo.delete(feed_id):
                raise HTTPException(status_code=404, detail="RSS feed not found")

    def execute(self, feed_id: int) -> RSSFeedExecuteResponse:
        with get_db() as conn:
            repo = RSSFeedRepository(conn)
            row = repo.find_by_id(feed_id)
            if row is None:
                raise HTTPException(status_code=404, detail="RSS feed not found")
            webhook_url = SettingsRepository(conn).get(WEBHOOK_SETTING_KEY)
            if not webhook_url:
                raise HTTPException(
                    status_code=400, detail="Webhook URL is not configured"
                )

            try:
                response = httpx.get(row["url"], timeout=5.0, follow_redirects=True)
            except httpx.HTTPError as exc:
                raise HTTPException(
                    status_code=422, detail="RSS feed URL is not reachable"
                ) from exc

            if response.status_code >= 400:
                raise HTTPException(
                    status_code=422, detail="RSS feed URL is not reachable"
                )

            parsed_feed = self._parse_rss_feed(response.content)
            feed_title = self._get_feed_title(parsed_feed, str(row["title"]))
            sent_urls = self._load_sent_article_urls(conn, feed_id)
            articles: list[dict[str, object]] = []
            embeds: list[dict[str, object]] = []
            for entry in parsed_feed.entries:
                entry_link = entry.get("link")
                if not entry_link or entry_link in sent_urls:
                    continue
                embed: dict[str, object] = {
                    "title": entry.get("title") or "(no title)",
                }
                embed["url"] = entry_link
                summary = entry.get("summary") or entry.get("description")
                if summary:
                    embed["description"] = summary
                embeds.append(embed)
                articles.append(
                    {
                        "url": entry_link,
                        "title": entry.get("title") or "(no title)",
                    }
                )

            if not embeds:
                return RSSFeedExecuteResponse(
                    feed_id=feed_id,
                    title=row["title"],
                    webhook_url=webhook_url,
                    delivered=True,
                    message="No new articles found.",
                )

            try:
                embed_chunks = self._chunk_embeds(embeds) or [[]]
                for index, chunk in enumerate(embed_chunks, start=1):
                    content = (
                        f"**{feed_title}** - **New articles** ({len(embeds)} items)"
                    )
                    if len(embed_chunks) > 1:
                        content = f"{content} [{index}]"
                    response = httpx.post(
                        webhook_url,
                        json={
                            "username": "Shiori Keeper",
                            "content": content,
                            "embeds": chunk,
                        },
                        timeout=5.0,
                    )
                    if response.status_code >= 400:
                        break
            except httpx.HTTPError:
                self._raise_discord_webhook_error()

            if response.status_code >= 400:
                self._raise_discord_webhook_error(response)

            self._record_sent_articles(conn, feed_id, articles)

            return RSSFeedExecuteResponse(
                feed_id=feed_id,
                title=row["title"],
                webhook_url=webhook_url,
                delivered=True,
                message=f"Posted {len(articles)} new article(s).",
            )
