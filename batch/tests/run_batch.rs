use rusqlite::Connection;
use shiori_keeper_batch::{
    fetch_webhook_urls, rss_periodic_execution_enabled, rss_webhook_notification_enabled, run_batch,
};

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
        CREATE TABLE webhook_endpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE rss_feeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            notify_webhook_enabled INTEGER NOT NULL DEFAULT 1,
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
        "INSERT INTO webhook_endpoints (url) VALUES (?)",
        ["https://discord.com/api/webhooks/1/token"],
    )
    .expect("insert webhook endpoint");

    conn.execute(
        "INSERT INTO app_settings (key, value, rss_periodic_execution_enabled) VALUES ('rss_periodic_execution_enabled', ?, ?)",
        (if enabled != 0 { "1" } else { "0" }, enabled),
    )
    .expect("insert settings");

    conn.execute(
        "INSERT INTO rss_feeds (id, url, title, description, notify_webhook_enabled) VALUES (1, ?, ?, ?, 1)",
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

#[tokio::test]
async fn disabled_rss_webhook_notification_returns_ok_without_fetching() {
    let conn = create_in_memory_test_db(1);
    conn.execute(
        "INSERT INTO app_settings (key, value, rss_periodic_execution_enabled) VALUES ('rss_webhook_notification_enabled', ?, ?)",
        ("0", 0),
    )
    .expect("insert notification setting");

    let result = run_batch(&conn).await;
    assert!(result.is_ok());
}

#[test]
fn rss_execution_settings_read_their_own_rows() {
    let conn = create_in_memory_test_db(1);
    conn.execute(
        "INSERT INTO app_settings (key, value, rss_periodic_execution_enabled) VALUES ('rss_webhook_notification_enabled', '1', 1)",
        [],
    )
    .expect("insert notification setting");

    assert!(rss_periodic_execution_enabled(&conn).expect("read periodic setting"));
    assert!(rss_webhook_notification_enabled(&conn).expect("read webhook notification setting"));
}

#[test]
fn fetch_webhook_urls_reads_multiple_endpoints_in_registration_order() {
    let conn = create_in_memory_test_db(1);
    conn.execute(
        "INSERT INTO webhook_endpoints (url) VALUES (?)",
        ["https://hooks.slack.com/services/xxx/yyy/zzz"],
    )
    .expect("insert second webhook endpoint");

    let urls = fetch_webhook_urls(&conn).expect("read webhook urls");
    assert_eq!(
        urls,
        vec![
            "https://discord.com/api/webhooks/1/token".to_string(),
            "https://hooks.slack.com/services/xxx/yyy/zzz".to_string(),
        ]
    );
}

#[test]
fn fetch_webhook_urls_falls_back_to_legacy_app_settings_key() {
    let conn = Connection::open_in_memory().expect("open in-memory db");
    conn.execute_batch(
        "
        CREATE TABLE app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            rss_periodic_execution_enabled INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        ",
    )
    .expect("create legacy schema");
    conn.execute(
        "INSERT INTO app_settings (key, value) VALUES ('default_webhook_url', ?)",
        ["https://discord.com/api/webhooks/1/token"],
    )
    .expect("insert legacy webhook setting");

    let urls = fetch_webhook_urls(&conn).expect("read webhook urls");
    assert_eq!(
        urls,
        vec!["https://discord.com/api/webhooks/1/token".to_string()]
    );
}
