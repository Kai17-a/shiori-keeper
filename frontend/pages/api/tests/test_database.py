"""Unit tests for database initialisation (Requirements 8.2)."""

import os
import sqlite3
import tempfile

from api.app.database import init_db


def test_init_db_creates_all_tables():
    """After calling init_db() on a fresh DB file, all 4 tables must exist."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        init_db(database_url=db_path)

        conn = sqlite3.connect(db_path)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        assert "bookmarks" in tables
        assert "folders" in tables
        assert "tags" in tables
        assert "bookmark_tags" in tables
    finally:
        os.unlink(db_path)


def test_init_db_is_idempotent():
    """Calling init_db() twice on the same DB must not raise an error."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    try:
        init_db(database_url=db_path)
        init_db(database_url=db_path)  # second call should be safe
    finally:
        os.unlink(db_path)


def test_db_error_returns_500(tmp_path, monkeypatch):
    """When DB operation fails, API should return 500 (Requirement 8.4)."""
    from fastapi.testclient import TestClient

    # Mock a DB operation that raises sqlite3.Error
    import api.app.repositories.bookmark_repo as br_module
    from api.app.main import app

    def mock_insert(*args, **kwargs):
        raise sqlite3.Error("Simulated DB error")

    monkeypatch.setattr(br_module.BookmarkRepository, "insert", mock_insert)

    client = TestClient(app)
    response = client.post(
        "/bookmarks", json={"url": "https://example.com", "title": "Test"}
    )

    assert response.status_code == 500
    assert "Database error" in response.json()["detail"]
