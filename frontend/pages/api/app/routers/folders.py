from fastapi import APIRouter, Depends

from api.app.models import FolderCreate, FolderResponse
from api.app.services.folder_service import FolderService

router = APIRouter(prefix="/folders", tags=["folders"])


def get_folder_service() -> FolderService:
    return FolderService()


@router.post("", status_code=201, response_model=FolderResponse)
def create_folder(body: FolderCreate, service: FolderService = Depends(get_folder_service)):
    return service.create(body)


@router.get("", status_code=200, response_model=list[FolderResponse])
def list_folders(service: FolderService = Depends(get_folder_service)):
    return service.list()


@router.delete("/{folder_id}", status_code=204)
def delete_folder(folder_id: int, service: FolderService = Depends(get_folder_service)):
    service.delete(folder_id)
