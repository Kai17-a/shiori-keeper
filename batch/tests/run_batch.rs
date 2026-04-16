use rusqlite::Connection;
use shiori_keeper_batch::run_batch;

fn create_in_memory_test_db(enabled: i64) -> Connection {
    let conn = Connection::open_in_memory().expect("open in-memory db");
    conn.execute_batch(
        "
        CREATE TABLE app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            rss_periodic_execution_enabled INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE rss_feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE rss_feed_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feed_id INTEGER NOT NULL REFERENCES rss_feeds(id) ON DELETE CASCADE,
            url TEXT NOT NULL,
            title TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            published DATETIME
        );
        ",
    )
    .expect("create schema");

    conn.execute(
        "INSERT INTO app_settings (key, value, rss_periodic_execution_enabled) VALUES ('default_webhook_url', ?, ?)",
        ("https://discord.com/api/webhooks/1/token", enabled),
    )
    .expect("insert settings");

    conn.execute(
        "INSERT INTO rss_feeds (id, url, title, description) VALUES (1, ?, ?, ?)",
        (
            "https://example.com/feed.xml",
            "Example Feed",
            Option::<&str>::None,
        ),
    )
    .expect("insert feed");

    conn
}

#[tokio::test]
async fn disabled_rss_periodic_execution_returns_ok_without_fetching() {
    let conn = create_in_memory_test_db(0);

    let result = run_batch(&conn).await;
    assert!(result.is_ok());
}
