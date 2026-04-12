import sqlite3
import xml.etree.ElementTree as ET

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


class RSSFeedService:
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

            self._validate_rss_feed_url(row["url"])

            try:
                response = httpx.post(
                    webhook_url,
                    json={
                        "username": "Bookmark Manager",
                        "content": f"RSS feed executed: {row['title']}\n{row['url']}",
                    },
                    timeout=5.0,
                )
            except httpx.HTTPError as exc:
                raise HTTPException(
                    status_code=502, detail="Failed to notify Discord webhook"
                ) from exc

            if response.status_code >= 400:
                raise HTTPException(
                    status_code=502, detail="Failed to notify Discord webhook"
                )

            return RSSFeedExecuteResponse(
                feed_id=feed_id,
                title=row["title"],
                webhook_url=webhook_url,
                delivered=True,
            )
