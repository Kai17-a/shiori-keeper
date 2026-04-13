from datetime import datetime
from typing import cast

from fastapi import HTTPException

from api.model.models import BookmarkResponse, TagResponse


class BookmarkServiceBase:
    def _raise_not_found(self, resource_name: str) -> None:
        raise HTTPException(status_code=404, detail=f"{resource_name} not found")

    def _build_bookmark_response(
        self, repo, row: dict[str, object]
    ) -> BookmarkResponse:
        bookmark_id = cast(int, row["id"])
        tags = [TagResponse(**tag) for tag in repo.get_tags(bookmark_id)]
        return BookmarkResponse(
            id=bookmark_id,
            url=cast(str, row["url"]),
            title=cast(str, row["title"]),
            description=cast(str | None, row["description"]),
            folder_id=cast(int | None, row["folder_id"]),
            is_favorite=cast(bool, row["is_favorite"]),
            tags=tags,
            created_at=cast(datetime, row["created_at"]),
            updated_at=cast(datetime, row["updated_at"]),
        )
