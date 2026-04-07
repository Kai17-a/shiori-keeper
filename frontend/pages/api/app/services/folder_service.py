from fastapi import HTTPException

from api.app.database import get_db
from api.app.models import FolderCreate, FolderResponse
from api.app.repositories.folder_repo import FolderRepository


class FolderService:
    def create(self, data: FolderCreate) -> FolderResponse:
        with get_db() as conn:
            repo = FolderRepository(conn)
            row = repo.insert(data.name)
            return FolderResponse(**row)

    def list(self) -> list[FolderResponse]:
        with get_db() as conn:
            repo = FolderRepository(conn)
            rows = repo.find_all()
            return [FolderResponse(**row) for row in rows]

    def delete(self, folder_id: int) -> None:
        with get_db() as conn:
            repo = FolderRepository(conn)
            found = repo.delete(folder_id)
            if not found:
                raise HTTPException(status_code=404, detail="Folder not found")
