from fastapi import APIRouter, Depends

from api.model.models import ErrorResponse, TagCreate, TagResponse, TagUpdate
from api.services.tag_service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


def get_tag_service() -> TagService:
    return TagService()


@router.post(
    "",
    status_code=201,
    response_model=TagResponse,
    responses={409: {"model": ErrorResponse, "description": "Tag name already exists"}},
)
def create_tag(body: TagCreate, service: TagService = Depends(get_tag_service)):
    return service.create(body)


@router.get("", status_code=200, response_model=list[TagResponse])
def list_tags(service: TagService = Depends(get_tag_service)):
    return service.list()


@router.patch(
    "/{tag_id}",
    response_model=TagResponse,
    responses={409: {"model": ErrorResponse, "description": "Tag name already exists"}},
)
def update_tag(tag_id: int, body: TagUpdate, service: TagService = Depends(get_tag_service)):
    return service.update(tag_id, body)


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, service: TagService = Depends(get_tag_service)):
    service.delete(tag_id)
