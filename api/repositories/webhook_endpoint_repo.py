import sqlite3


class WebhookEndpointRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def find_all(self) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT id, name, url, created_at, updated_at
            FROM webhook_endpoints
            ORDER BY id ASC
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def insert(self, name: str, url: str) -> dict:
        cursor = self.conn.execute(
            "INSERT INTO webhook_endpoints (name, url) VALUES (?, ?)",
            (name, url),
        )
        row = self.conn.execute(
            """
            SELECT id, name, url, created_at, updated_at
            FROM webhook_endpoints
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)

    def find_by_id(self, webhook_id: int) -> dict | None:
        row = self.conn.execute(
            """
            SELECT id, name, url, created_at, updated_at
            FROM webhook_endpoints
            WHERE id = ?
            """,
            (webhook_id,),
        ).fetchone()
        return dict(row) if row else None

    def delete(self, webhook_id: int) -> bool:
        cursor = self.conn.execute(
            "DELETE FROM webhook_endpoints WHERE id = ?",
            (webhook_id,),
        )
        return cursor.rowcount > 0
