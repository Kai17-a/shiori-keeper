import sqlite3


class RSSFeedRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def insert(self, url: str, title: str, description: str | None) -> dict:
        cursor = self.conn.execute(
            "INSERT INTO rss_feeds (url, title, description) VALUES (?, ?, ?)",
            (url, title, description),
        )
        row = self.conn.execute(
            "SELECT * FROM rss_feeds WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)

    def count_all(self, q: str | None = None) -> int:
        query = "SELECT COUNT(*) AS total FROM rss_feeds"
        params: list = []
        if q is not None:
            query += " WHERE (title LIKE ? OR url LIKE ?)"
            like = f"%{q}%"
            params.extend([like, like])
        row = self.conn.execute(query, params).fetchone()
        return int(row["total"]) if row else 0

    def find_all(self, q: str | None, limit: int, offset: int) -> list[dict]:
        query = "SELECT * FROM rss_feeds"
        params: list = []
        if q is not None:
            query += " WHERE (title LIKE ? OR url LIKE ?)"
            like = f"%{q}%"
            params.extend([like, like])
        query += " ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def find_by_id(self, feed_id: int) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM rss_feeds WHERE id = ?", (feed_id,)
        ).fetchone()
        return dict(row) if row else None

    def find_by_url(self, url: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM rss_feeds WHERE url = ?", (url,)
        ).fetchone()
        return dict(row) if row else None

    def update(self, feed_id: int, fields: dict) -> dict | None:
        if not fields:
            return self.find_by_id(feed_id)
        set_clauses = ", ".join(f"{key} = ?" for key in fields)
        set_clauses += ", updated_at = strftime('%Y-%m-%d %H:%M:%f', 'now')"
        params = list(fields.values()) + [feed_id]
        cursor = self.conn.execute(
            f"UPDATE rss_feeds SET {set_clauses} WHERE id = ?", params
        )
        if cursor.rowcount == 0:
            return None
        return self.find_by_id(feed_id)

    def delete(self, feed_id: int) -> bool:
        cursor = self.conn.execute("DELETE FROM rss_feeds WHERE id = ?", (feed_id,))
        return cursor.rowcount > 0
