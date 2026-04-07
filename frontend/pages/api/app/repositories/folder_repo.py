import sqlite3


class FolderRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def insert(self, name: str) -> dict:
        cursor = self.conn.execute(
            "INSERT INTO folders (name) VALUES (?)", (name,)
        )
        row = self.conn.execute(
            "SELECT * FROM folders WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)

    def find_all(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM folders").fetchall()
        return [dict(row) for row in rows]

    def find_by_id(self, folder_id: int) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM folders WHERE id = ?", (folder_id,)
        ).fetchone()
        return dict(row) if row else None

    def delete(self, folder_id: int) -> bool:
        cursor = self.conn.execute(
            "DELETE FROM folders WHERE id = ?", (folder_id,)
        )
        return cursor.rowcount > 0
