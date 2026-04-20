from datetime import datetime
from typing import ClassVar

from pydantic import AnyHttpUrl, BaseModel, Field as PydField, field_validator
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlmodel import Field, SQLModel


# --- SQLModel table models ---


class Folder(SQLModel, table=True):
    __tablename__: ClassVar[str] = "folders"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String, nullable=False, unique=True))
    description: str | None = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("(datetime('now'))"),
        )
    )


class Bookmark(SQLModel, table=True):
    __tablename__: ClassVar[str] = "bookmarks"
    __table_args__ = (Index("idx_bookmarks_url_unique", "url", unique=True),)

    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(sa_column=Column(String, nullable=False))
    title: str = Field(sa_column=Column(String, nullable=False))
    description: str | None = Field(default=None, sa_column=Column(Text))
    folder_id: int | None = Field(
        default=None,
        sa_column=Column(
            Integer,
            ForeignKey("folders.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    is_favorite: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, server_default=text("0")),
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("(datetime('now'))"),
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("(datetime('now'))"),
        )
    )


class RSSFeed(SQLModel, table=True):
    __tablename__: ClassVar[str] = "rss_feeds"
    __table_args__ = (Index("idx_rss_feeds_url_unique", "url", unique=True),)

    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(sa_column=Column(String, nullable=False))
    title: str = Field(sa_column=Column(String, nullable=False))
    description: str | None = Field(default=None, sa_column=Column(Text))
    notify_webhook_enabled: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default=text("1")),
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("(datetime('now'))"),
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("(datetime('now'))"),
        )
    )


class RSSFeedArticle(SQLModel, table=True):
    __tablename__: ClassVar[str] = "rss_feed_articles"
    __table_args__ = (
        Index("idx_rss_feed_articles_feed_url_unique", "feed_id", "url", unique=True),
    )

    id: int | None = Field(default=None, primary_key=True)
    feed_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("rss_feeds.id", ondelete="CASCADE"),
            nullable=False,
        )
    )
    url: str = Field(sa_column=Column(String, nullable=False))
    title: str | None = Field(default=None, sa_column=Column(String))
    published: datetime | None = Field(default=None, sa_column=Column(DateTime))
    created_at: datetime = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("(datetime('now'))"),
        )
    )


class AppSetting(SQLModel, table=True):
    __tablename__: ClassVar[str] = "app_settings"

    key: str = Field(primary_key=True)
    value: str = Field(sa_column=Column(Text, nullable=False))
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime,
            nullable=False,
            server_default=text("(datetime('now'))"),
        )
    )


class Tag(SQLModel, table=True):
    __tablename__: ClassVar[str] = "tags"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String, nullable=False, unique=True))
    description: str | None = Field(default=None, sa_column=Column(Text))


class BookmarkTag(SQLModel, table=True):
    __tablename__: ClassVar[str] = "bookmark_tags"

    bookmark_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("bookmarks.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    tag_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )


# --- Request schemas ---


class BookmarkCreate(BaseModel):
    url: AnyHttpUrl
    title: str = PydField(min_length=1)
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
    title: str | None = PydField(default=None, min_length=1)
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
    name: str = PydField(min_length=1)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value


class FolderUpdate(BaseModel):
    name: str | None = PydField(default=None, min_length=1)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value


class TagCreate(BaseModel):
    name: str = PydField(min_length=1)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value


class TagUpdate(BaseModel):
    name: str | None = PydField(default=None, min_length=1)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value


class TagAttach(BaseModel):
    tag_id: int = PydField(gt=0)


class BookmarkFavoriteUpdate(BaseModel):
    bookmark_id: int = PydField(gt=0)
    is_favorite: bool


class RSSFeedCreate(BaseModel):
    url: AnyHttpUrl
    title: str = PydField(min_length=1)
    description: str | None = None
    notify_webhook_enabled: bool = True

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be empty")
        return value


class RSSFeedUpdate(BaseModel):
    url: AnyHttpUrl | None = None
    title: str | None = PydField(default=None, min_length=1)
    description: str | None = None
    notify_webhook_enabled: bool | None = None

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
    notify_webhook_enabled: bool
    created_at: datetime
    updated_at: datetime


class RSSFeedArticleResponse(BaseModel):
    id: int
    feed_id: int
    url: str
    title: str | None = None
    published: datetime | None = None
    created_at: datetime


class RSSFeedArticleListResponse(BaseModel):
    items: list[RSSFeedArticleResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


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
    message: str | None = None


class SettingsWebhookUpdate(BaseModel):
    webhook_url: AnyHttpUrl


class SettingsWebhookResponse(BaseModel):
    webhook_url: str


class SettingsWebhookPingRequest(BaseModel):
    webhook_url: str


class SettingsWebhookPingResponse(BaseModel):
    pong: bool


class SettingsRssExecutionResponse(BaseModel):
    enabled: bool


class SettingsRssExecutionUpdate(BaseModel):
    enabled: bool


class SettingsRssWebhookNotificationResponse(BaseModel):
    enabled: bool


class SettingsRssWebhookNotificationUpdate(BaseModel):
    enabled: bool


class DashboardMetricsResponse(BaseModel):
    bookmarks_total: int
    folders_total: int
    tags_total: int
    favorites_total: int
    rss_feeds_total: int


class ErrorResponse(BaseModel):
    detail: str
