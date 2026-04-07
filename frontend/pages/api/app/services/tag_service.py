import sqlite3

from fastapi import HTTPException

from api.app.database import get_db
from api.app.models import TagCreate, TagResponse
from api.app.repositories.tag_repo import TagRepository


class TagService:
    def create(self, data: TagCreate) -> TagResponse:
        with get_db() as conn:
            repo = TagRepository(conn)
            try:
                row = repo.insert(data.name)
            except sqlite3.IntegrityError:
                raise HTTPException(status_code=409, detail="Tag name already exists")
            return TagResponse(**row)

    def list(self) -> list[TagResponse]:
        with get_db() as conn:
            repo = TagRepository(conn)
            rows = repo.find_all()
            return [TagResponse(**row) for row in rows]

    def delete(self, tag_id: int) -> None:
        with get_db() as conn:
            repo = TagRepository(conn)
            found = repo.delete(tag_id)
            if not found:
                raise HTTPException(status_code=404, detail="Tag not found")
