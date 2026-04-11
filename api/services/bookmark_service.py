import sqlite3

from fastapi import HTTPException

from api.database import get_db
from api.model.models import (
    BookmarkCreate,
    BookmarkListResponse,
    BookmarkResponse,
    BookmarkUpdate,
    TagResponse,
)
from api.repositories.bookmark_repo import BookmarkRepository
from api.repositories.folder_repo import FolderRepository
from api.repositories.tag_repo import TagRepository


class BookmarkService:
    def _to_response(self, repo: BookmarkRepository, row: dict) -> BookmarkResponse:
        tags = [TagResponse(**t) for t in repo.get_tags(row["id"])]
        return BookmarkResponse(**row, tags=tags)

    def _verify_folder(self, conn, folder_id: int) -> None:
        folder_repo = FolderRepository(conn)
        if folder_repo.find_by_id(folder_id) is None:
            raise HTTPException(status_code=404, detail="Folder not found")

    def _verify_tags(self, conn, tag_ids: list[int]) -> None:
        tag_repo = TagRepository(conn)
        missing = [tag_id for tag_id in tag_ids if tag_repo.find_by_id(tag_id) is None]
        if missing:
            raise HTTPException(status_code=404, detail="Tag not found")

    def _sync_tags(self, repo: BookmarkRepository, bookmark_id: int, tag_ids: list[int] | None) -> None:
        if tag_ids is None:
            return
        unique_tag_ids = list(dict.fromkeys(tag_ids))
        self._verify_tags(repo.conn, unique_tag_ids)
        repo.set_tags(bookmark_id, unique_tag_ids)

    def create(self, data: BookmarkCreate) -> BookmarkResponse:
        with get_db() as conn:
            if data.folder_id is not None:
                self._verify_folder(conn, data.folder_id)
            repo = BookmarkRepository(conn)
            if repo.find_by_url(str(data.url)) is not None:
                raise HTTPException(status_code=409, detail="Bookmark URL already exists")
            row = repo.insert(
                url=str(data.url),
                title=data.title,
                description=data.description,
                folder_id=data.folder_id,
            )
            self._sync_tags(repo, row["id"], data.tag_ids)
            row = repo.find_by_id(row["id"])
            return self._to_response(repo, row)

    def list(
        self,
        folder_id: int | None = None,
        tag_id: int | None = None,
        q: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> BookmarkListResponse:
        with get_db() as conn:
            repo = BookmarkRepository(conn)
            total = repo.count_all(folder_id=folder_id, tag_id=tag_id, q=q)
            total_pages = max((total + per_page - 1) // per_page, 1) if total else 0
            page = max(page, 1)
            if total_pages and page > total_pages:
                page = total_pages
            offset = (page - 1) * per_page
            rows = repo.find_all(folder_id=folder_id, tag_id=tag_id, q=q, limit=per_page, offset=offset)
            items = [self._to_response(repo, row) for row in rows]
            return BookmarkListResponse(
                items=items,
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
            )

    def get(self, bookmark_id: int) -> BookmarkResponse:
        with get_db() as conn:
            repo = BookmarkRepository(conn)
            row = repo.find_by_id(bookmark_id)
            if row is None:
                raise HTTPException(status_code=404, detail="Bookmark not found")
            return self._to_response(repo, row)

    def update(self, bookmark_id: int, data: BookmarkUpdate) -> BookmarkResponse:
        with get_db() as conn:
            # Verify bookmark exists first
            repo = BookmarkRepository(conn)
            if repo.find_by_id(bookmark_id) is None:
                raise HTTPException(status_code=404, detail="Bookmark not found")

            # Build fields dict with only non-None values
            fields: dict = {}
            if data.url is not None:
                fields["url"] = str(data.url)
            if data.title is not None:
                fields["title"] = data.title
            if data.description is not None:
                fields["description"] = data.description
            if data.folder_id is not None:
                self._verify_folder(conn, data.folder_id)
                fields["folder_id"] = data.folder_id
            if data.url is not None:
                existing = repo.find_by_url(str(data.url))
                if existing is not None and existing["id"] != bookmark_id:
                    raise HTTPException(status_code=409, detail="Bookmark URL already exists")

            row = repo.update(bookmark_id, fields)
            self._sync_tags(repo, bookmark_id, data.tag_ids)
            row = repo.find_by_id(bookmark_id)
            return self._to_response(repo, row)

    def delete(self, bookmark_id: int) -> None:
        with get_db() as conn:
            repo = BookmarkRepository(conn)
            found = repo.delete(bookmark_id)
            if not found:
                raise HTTPException(status_code=404, detail="Bookmark not found")

    def add_tag(self, bookmark_id: int, tag_id: int) -> BookmarkResponse:
        with get_db() as conn:
            repo = BookmarkRepository(conn)
            if repo.find_by_id(bookmark_id) is None:
                raise HTTPException(status_code=404, detail="Bookmark not found")

            tag_repo = TagRepository(conn)
            if tag_repo.find_by_id(tag_id) is None:
                raise HTTPException(status_code=404, detail="Tag not found")

            try:
                repo.add_tag(bookmark_id, tag_id)
            except sqlite3.IntegrityError:
                raise HTTPException(status_code=409, detail="Tag already attached")

            row = repo.find_by_id(bookmark_id)
            return self._to_response(repo, row)

    def remove_tag(self, bookmark_id: int, tag_id: int) -> None:
        with get_db() as conn:
            repo = BookmarkRepository(conn)
            if repo.find_by_id(bookmark_id) is None:
                raise HTTPException(status_code=404, detail="Bookmark not found")

            removed = repo.remove_tag(bookmark_id, tag_id)
            if not removed:
                raise HTTPException(status_code=404, detail="Tag not attached")
