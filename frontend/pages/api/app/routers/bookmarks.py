from fastapi import APIRouter, Depends

from api.app.models import BookmarkCreate, BookmarkResponse, BookmarkUpdate
from api.app.services.bookmark_service import BookmarkService

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


def get_bookmark_service() -> BookmarkService:
    return BookmarkService()


@router.post("", status_code=201, response_model=BookmarkResponse)
def create_bookmark(body: BookmarkCreate, service: BookmarkService = Depends(get_bookmark_service)):
    return service.create(body)


@router.get("", status_code=200, response_model=list[BookmarkResponse])
def list_bookmarks(
    folder_id: int | None = None,
    tag_id: int | None = None,
    q: str | None = None,
    service: BookmarkService = Depends(get_bookmark_service),
):
    return service.list(folder_id=folder_id, tag_id=tag_id, q=q)


@router.get("/{bookmark_id}", status_code=200, response_model=BookmarkResponse)
def get_bookmark(bookmark_id: int, service: BookmarkService = Depends(get_bookmark_service)):
    return service.get(bookmark_id)


@router.patch("/{bookmark_id}", status_code=200, response_model=BookmarkResponse)
def update_bookmark(
    bookmark_id: int,
    body: BookmarkUpdate,
    service: BookmarkService = Depends(get_bookmark_service),
):
    return service.update(bookmark_id, body)


@router.delete("/{bookmark_id}", status_code=204)
def delete_bookmark(bookmark_id: int, service: BookmarkService = Depends(get_bookmark_service)):
    service.delete(bookmark_id)
