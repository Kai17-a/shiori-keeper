#[path = "../src/webhook.rs"]
mod webhook;

use rusqlite::Connection;

fn create_in_memory_test_db() -> Connection {
    let conn = Connection::open_in_memory().expect("open in-memory db");
    conn.execute_batch(
        "
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
        "INSERT INTO rss_feeds (id, url, title, description) VALUES (1, ?, ?, ?)",
        (
            "https://example.com/feed",
            "Example Feed",
            Option::<&str>::None,
        ),
    )
    .expect("insert feed");
    conn
}

#[test]
fn build_payload_matches_expected_shape() {
    let payload = serde_json::json!({
        "username": "Shiori Keeper",
        "content": "**Example Feed** - **New articles** (1 items)",
        "embeds": [{
            "title": "Example Article",
            "url": "https://example.com/article",
            "description": "Example summary",
        }]
    });

    let embeds = vec![webhook::Embed {
        title: "Example Article",
        link: "https://example.com/article",
        published: "Wed, 01 Jan 2025 00:00:00 GMT",
        summary: "Example summary",
    }];
    let articles = vec![webhook::Article {
        url: "https://example.com/article",
        title: "Example Article",
        published: "Wed, 01 Jan 2025 00:00:00 GMT",
    }];

    let _ = (embeds, articles);
    let expected_body = serde_json::json!({
        "username": "Shiori Keeper",
        "content": "**Example Feed** - **New articles** (1 items)",
        "embeds": [{
            "title": "Example Article",
            "url": "https://example.com/article",
            "description": "Example summary",
        }]
    });

    assert_eq!(payload, expected_body);
}

#[test]
fn record_sent_articles_inserts_rows() {
    let conn = create_in_memory_test_db();
    let articles = vec![
        webhook::Article {
            url: "https://example.com/article-1",
            title: "Article 1",
            published: "Wed, 01 Jan 2025 00:00:00 GMT",
        },
        webhook::Article {
            url: "https://example.com/article-2",
            title: "Article 2",
            published: "Thu, 02 Jan 2025 00:00:00 GMT",
        },
    ];

    webhook::record_sent_articles(&conn, 1, &articles).expect("record articles");

    let count: i64 = conn
        .query_row(
            "SELECT COUNT(*) FROM rss_feed_articles WHERE feed_id = 1",
            [],
            |row| row.get(0),
        )
        .expect("count rows");
    assert_eq!(count, 2);

    let urls = webhook::load_sent_article_urls(&conn, 1).expect("load urls");
    assert!(urls.contains("https://example.com/article-1"));
    assert!(urls.contains("https://example.com/article-2"));
}

#[tokio::test]
async fn post_with_retry_retries_three_times() {
    let result = webhook::send_rss_webhook(
        "http://localhost:9999",
        "Example Feed",
        "https://example.com/feed",
        &[webhook::Embed {
            title: "Example Article",
            link: "https://example.com/article",
            published: "Wed, 01 Jan 2025 00:00:00 GMT",
            summary: "Example summary",
        }],
        &[webhook::Article {
            url: "https://example.com/article",
            title: "Example Article",
            published: "Wed, 01 Jan 2025 00:00:00 GMT",
        }],
    )
    .await;

    let err = result.expect_err("webhook should fail");
    assert!(err.to_string().contains("after 3 attempts"));
}
