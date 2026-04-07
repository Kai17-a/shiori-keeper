import sqlite3


class BookmarkRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def insert(self, url: str, title: str, description: str | None, folder_id: int | None) -> dict:
        cursor = self.conn.execute(
            "INSERT INTO bookmarks (url, title, description, folder_id) VALUES (?, ?, ?, ?)",
            (url, title, description, folder_id),
        )
        row = self.conn.execute(
            "SELECT * FROM bookmarks WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)

    def find_all(self, folder_id: int | None, tag_id: int | None, q: str | None) -> list[dict]:
        query = "SELECT DISTINCT b.* FROM bookmarks b"
        params: list = []

        if tag_id is not None:
            query += " INNER JOIN bookmark_tags bt ON b.id = bt.bookmark_id"

        conditions: list[str] = []
        if folder_id is not None:
            conditions.append("b.folder_id = ?")
            params.append(folder_id)
        if tag_id is not None:
            conditions.append("bt.tag_id = ?")
            params.append(tag_id)
        if q is not None:
            conditions.append("(b.title LIKE ? OR b.url LIKE ?)")
            like = f"%{q}%"
            params.extend([like, like])

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def find_by_id(self, bookmark_id: int) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM bookmarks WHERE id = ?", (bookmark_id,)
        ).fetchone()
        return dict(row) if row else None

    def update(self, bookmark_id: int, fields: dict) -> dict | None:
        if not fields:
            return self.find_by_id(bookmark_id)

        set_clauses = ", ".join(f"{key} = ?" for key in fields)
        set_clauses += ", updated_at = datetime('now')"
        params = list(fields.values()) + [bookmark_id]

        cursor = self.conn.execute(
            f"UPDATE bookmarks SET {set_clauses} WHERE id = ?", params
        )
        if cursor.rowcount == 0:
            return None
        return self.find_by_id(bookmark_id)

    def delete(self, bookmark_id: int) -> bool:
        # bookmark_tags rows are removed automatically via ON DELETE CASCADE
        cursor = self.conn.execute(
            "DELETE FROM bookmarks WHERE id = ?", (bookmark_id,)
        )
        return cursor.rowcount > 0

    def add_tag(self, bookmark_id: int, tag_id: int) -> None:
        # Let sqlite3.IntegrityError propagate on duplicate (PRIMARY KEY violation)
        self.conn.execute(
            "INSERT INTO bookmark_tags (bookmark_id, tag_id) VALUES (?, ?)",
            (bookmark_id, tag_id),
        )

    def remove_tag(self, bookmark_id: int, tag_id: int) -> bool:
        cursor = self.conn.execute(
            "DELETE FROM bookmark_tags WHERE bookmark_id = ? AND tag_id = ?",
            (bookmark_id, tag_id),
        )
        return cursor.rowcount > 0

    def get_tags(self, bookmark_id: int) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT t.id, t.name
            FROM tags t
            INNER JOIN bookmark_tags bt ON t.id = bt.tag_id
            WHERE bt.bookmark_id = ?
            """,
            (bookmark_id,),
        ).fetchall()
        return [dict(row) for row in rows]
