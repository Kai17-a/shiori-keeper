from fastapi import APIRouter, Depends

from api.app.models import TagCreate, TagResponse
from api.app.services.tag_service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


def get_tag_service() -> TagService:
    return TagService()


@router.post("", status_code=201, response_model=TagResponse)
def create_tag(body: TagCreate, service: TagService = Depends(get_tag_service)):
    return service.create(body)


@router.get("", status_code=200, response_model=list[TagResponse])
def list_tags(service: TagService = Depends(get_tag_service)):
    return service.list()


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, service: TagService = Depends(get_tag_service)):
    service.delete(tag_id)
