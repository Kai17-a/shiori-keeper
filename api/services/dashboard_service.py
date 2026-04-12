from api.database import get_db
from api.model.models import DashboardMetricsResponse


class DashboardService:
    def metrics(self) -> DashboardMetricsResponse:
        with get_db() as conn:
            bookmarks_total = conn.execute(
                "SELECT COUNT(*) AS total FROM bookmarks"
            ).fetchone()["total"]
            folders_total = conn.execute(
                "SELECT COUNT(*) AS total FROM folders"
            ).fetchone()["total"]
            tags_total = conn.execute(
                "SELECT COUNT(*) AS total FROM tags"
            ).fetchone()["total"]
            favorites_total = conn.execute(
                "SELECT COUNT(*) AS total FROM bookmarks WHERE is_favorite = 1"
            ).fetchone()["total"]

            return DashboardMetricsResponse(
                bookmarks_total=int(bookmarks_total),
                folders_total=int(folders_total),
                tags_total=int(tags_total),
                favorites_total=int(favorites_total),
            )
