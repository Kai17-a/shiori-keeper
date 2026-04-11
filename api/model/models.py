from datetime import datetime
from pydantic import AnyHttpUrl, BaseModel, Field, field_validator


# --- Request schemas ---

class BookmarkCreate(BaseModel):
    url: AnyHttpUrl
    title: str = Field(min_length=1)
    description: str | None = None
    folder_id: int | None = None
    tag_ids: list[int] | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be empty")
        return value

    @field_validator("tag_ids")
    @classmethod
    def validate_tag_ids(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return value
        if len(value) != len(set(value)):
            raise ValueError("tag_ids must not contain duplicates")
        return value


class BookmarkUpdate(BaseModel):
    url: AnyHttpUrl | None = None
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    folder_id: int | None = None
    tag_ids: list[int] | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be empty")
        return value

    @field_validator("tag_ids")
    @classmethod
    def validate_tag_ids(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return value
        if len(value) != len(set(value)):
            raise ValueError("tag_ids must not contain duplicates")
        return value


class FolderCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value


class FolderUpdate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value


class TagCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value


class TagUpdate(BaseModel):
    name: str = Field(min_length=1)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value


class TagAttach(BaseModel):
    tag_id: int = Field(gt=0)


# --- Response schemas ---

class TagResponse(BaseModel):
    id: int
    name: str
    description: str | None = None


class FolderResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
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


class BookmarkListResponse(BaseModel):
    items: list[BookmarkResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class ErrorResponse(BaseModel):
    detail: str
