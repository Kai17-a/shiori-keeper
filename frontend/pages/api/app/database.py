import sqlite3
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv("DATABASE_URL", "bookmarks.db")


def init_db(database_url: str = DATABASE_URL) -> None:
    """Create all tables if they don't exist."""
    conn = sqlite3.connect(database_url)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS folders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS bookmarks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                url         TEXT    NOT NULL,
                title       TEXT    NOT NULL,
                description TEXT,
                folder_id   INTEGER REFERENCES folders(id) ON DELETE SET NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS tags (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS bookmark_tags (
                bookmark_id INTEGER NOT NULL REFERENCES bookmarks(id) ON DELETE CASCADE,
                tag_id      INTEGER NOT NULL REFERENCES tags(id)      ON DELETE CASCADE,
                PRIMARY KEY (bookmark_id, tag_id)
            );
        """)
        conn.commit()
    finally:
        conn.close()


@contextmanager
def get_db(database_url: str = DATABASE_URL):
    """Yield a SQLite connection with foreign keys enabled and auto commit/rollback."""
    conn = sqlite3.connect(database_url)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
