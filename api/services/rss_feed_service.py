import sqlite3

from fastapi import HTTPException

from api.database import get_db
from api.model.models import RSSFeedCreate, RSSFeedListResponse, RSSFeedResponse, RSSFeedUpdate
from api.repositories.rss_feed_repo import RSSFeedRepository


class RSSFeedService:
    def create(self, data: RSSFeedCreate) -> RSSFeedResponse:
        with get_db() as conn:
            repo = RSSFeedRepository(conn)
            if repo.find_by_url(str(data.url)) is not None:
                raise HTTPException(status_code=409, detail="RSS feed URL already exists")
            try:
                row = repo.insert(str(data.url), data.title, data.description)
            except sqlite3.IntegrityError:
                raise HTTPException(status_code=409, detail="RSS feed URL already exists")
            return RSSFeedResponse(**row)

    def list(self, q: str | None = None, page: int = 1, per_page: int = 20) -> RSSFeedListResponse:
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
            return RSSFeedListResponse(items=items, total=total, page=page, per_page=per_page, total_pages=total_pages)

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
                    raise HTTPException(status_code=409, detail="RSS feed URL already exists")
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
