from api.services.bookmark_service import BookmarkService
from api.services.folder_service import FolderService
from api.services.rss_feed_service import RSSFeedService
from api.services.tag_service import TagService


def get_bookmark_service() -> BookmarkService:
    return BookmarkService()


def get_folder_service() -> FolderService:
    return FolderService()


def get_rss_feed_service() -> RSSFeedService:
    return RSSFeedService()


def get_tag_service() -> TagService:
    return TagService()
