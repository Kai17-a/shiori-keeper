import sqlite3
from contextlib import contextmanager

DATABASE_URL = "bookmarks.db"


def init_db(database_url: str = DATABASE_URL) -> None:
    """Create all tables if they don't exist."""
    conn = sqlite3.connect(database_url)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS folders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                description TEXT,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS bookmarks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                url         TEXT    NOT NULL,
                title       TEXT    NOT NULL,
                description TEXT,
                folder_id   INTEGER REFERENCES folders(id) ON DELETE SET NULL,
                is_favorite INTEGER NOT NULL DEFAULT 0,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS rss_feeds (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                url         TEXT    NOT NULL,
                title       TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS rss_feed_articles (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id     INTEGER NOT NULL REFERENCES rss_feeds(id) ON DELETE CASCADE,
                url         TEXT    NOT NULL,
                title       TEXT,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS app_settings (
                key         TEXT    PRIMARY KEY,
                value       TEXT    NOT NULL,
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS tags (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS bookmark_tags (
                bookmark_id INTEGER NOT NULL REFERENCES bookmarks(id) ON DELETE CASCADE,
                tag_id      INTEGER NOT NULL REFERENCES tags(id)      ON DELETE CASCADE,
                PRIMARY KEY (bookmark_id, tag_id)
            );
        """)
        conn.execute(
            """
            DELETE FROM bookmarks
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM bookmarks
                GROUP BY url
            )
            """
        )
        conn.execute(
            """
            DELETE FROM folders
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM folders
                GROUP BY name
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_bookmarks_url_unique
            ON bookmarks(url)
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_rss_feeds_url_unique
            ON rss_feeds(url)
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_rss_feed_articles_feed_url_unique
            ON rss_feed_articles(feed_id, url)
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_folders_name_unique
            ON folders(name)
            """
        )
        folder_columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(folders)").fetchall()
        }
        if "description" not in folder_columns:
            conn.execute("ALTER TABLE folders ADD COLUMN description TEXT")
        bookmark_columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(bookmarks)").fetchall()
        }
        if "is_favorite" not in bookmark_columns:
            conn.execute("ALTER TABLE bookmarks ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0")
            conn.execute("UPDATE bookmarks SET is_favorite = 0 WHERE is_favorite IS NULL")
        rss_feed_columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(rss_feeds)").fetchall()
        }
        if "description" not in rss_feed_columns:
            conn.execute("ALTER TABLE rss_feeds ADD COLUMN description TEXT")
        tag_columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(tags)").fetchall()
        }
        if "description" not in tag_columns:
            conn.execute("ALTER TABLE tags ADD COLUMN description TEXT")
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
