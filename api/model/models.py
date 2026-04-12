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


class BookmarkFavoriteUpdate(BaseModel):
    bookmark_id: int = Field(gt=0)
    is_favorite: bool


class RSSFeedCreate(BaseModel):
    url: AnyHttpUrl
    title: str = Field(min_length=1)
    description: str | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be empty")
        return value


class RSSFeedUpdate(BaseModel):
    url: AnyHttpUrl | None = None
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be empty")
        return value


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
    is_favorite: bool
    tags: list[TagResponse]
    created_at: datetime
    updated_at: datetime


class BookmarkListResponse(BaseModel):
    items: list[BookmarkResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class RSSFeedResponse(BaseModel):
    id: int
    url: str
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class RSSFeedListResponse(BaseModel):
    items: list[RSSFeedResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class RSSFeedExecuteResponse(BaseModel):
    feed_id: int
    title: str
    webhook_url: str
    delivered: bool


class SettingsWebhookUpdate(BaseModel):
    webhook_url: AnyHttpUrl


class SettingsWebhookResponse(BaseModel):
    webhook_url: str


class SettingsWebhookPingRequest(BaseModel):
    webhook_url: AnyHttpUrl


class SettingsWebhookPingResponse(BaseModel):
    pong: bool


class DashboardMetricsResponse(BaseModel):
    bookmarks_total: int
    folders_total: int
    tags_total: int
    favorites_total: int
    rss_feeds_total: int


class ErrorResponse(BaseModel):
    detail: str
