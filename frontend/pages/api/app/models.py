from datetime import datetime
from pydantic import AnyHttpUrl, BaseModel


# --- Request schemas ---

class BookmarkCreate(BaseModel):
    url: AnyHttpUrl
    title: str
    description: str | None = None
    folder_id: int | None = None


class BookmarkUpdate(BaseModel):
    url: AnyHttpUrl | None = None
    title: str | None = None
    description: str | None = None
    folder_id: int | None = None


class FolderCreate(BaseModel):
    name: str


class TagCreate(BaseModel):
    name: str


class TagAttach(BaseModel):
    tag_id: int


# --- Response schemas ---

class TagResponse(BaseModel):
    id: int
    name: str


class FolderResponse(BaseModel):
    id: int
    name: str
    created_at: datetime


class BookmarkResponse(BaseModel):
    id: int
    url: str
    title: str
    description: str | None
    folder_id: int | None
    tags: list[TagResponse]
    created_at: datetime
    updated_at: datetime
