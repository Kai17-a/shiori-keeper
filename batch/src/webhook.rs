use std::error::Error;
use std::io;
use std::time::Duration;

use rusqlite::{Connection, params};

#[derive(Debug)]
pub struct Embed<'a> {
    pub title: &'a str,
    pub link: &'a str,
    pub published: &'a str,
    pub summary: &'a str,
}

#[derive(Debug)]
pub struct Article<'a> {
    pub url: &'a str,
    pub title: &'a str,
    pub published: &'a str,
}

fn has_published_column(conn: &Connection) -> Result<bool, rusqlite::Error> {
    let mut stmt = conn.prepare("PRAGMA table_info(rss_feed_articles)")?;
    let rows = stmt.query_map([], |row| row.get::<_, String>(1))?;
    for row in rows {
        if row? == "published" {
            return Ok(true);
        }
    }
    Ok(false)
}

fn chunk_embeds<'a>(embeds: &'a [Embed<'a>]) -> Vec<Vec<&'a Embed<'a>>> {
    let mut chunks = Vec::new();
    let mut current = Vec::new();
    let mut current_len = 0usize;

    for embed in embeds {
        let embed_len =
            embed.title.len() + embed.link.len() + embed.published.len() + embed.summary.len();
        if (current.len() >= 10 || current_len + embed_len > 6000) && !current.is_empty() {
            chunks.push(current);
            current = Vec::new();
            current_len = 0;
        }
        current.push(embed);
        current_len += embed_len;
    }

    if !current.is_empty() {
        chunks.push(current);
    }

    chunks
}

fn build_payload(content: String, embeds_payload: Vec<serde_json::Value>) -> serde_json::Value {
    serde_json::json!({
        "username": "Shiori Keeper",
        "content": content,
        "embeds": embeds_payload,
    })
}

async fn post_with_retry(
    client: &reqwest::Client,
    webhook_url: &str,
    payload: &serde_json::Value,
) -> Result<reqwest::Response, String> {
    let mut last_error: Option<String> = None;
    for attempt in 1..=3 {
        match client.post(webhook_url).json(payload).send().await {
            Ok(response) => return Ok(response),
            Err(err) => {
                last_error = Some(err.to_string());
                if attempt < 3 {
                    tokio::time::sleep(Duration::from_millis(500)).await;
                }
            }
        }
    }

    Err(last_error.unwrap_or_else(|| "unknown error".to_string()))
}

pub async fn send_rss_webhook(
    webhook_url: &str,
    feed_title: &str,
    feed_url: &str,
    embeds: &[Embed<'_>],
    articles: &[Article<'_>],
) -> Result<(), Box<dyn Error>> {
    let client = reqwest::Client::new();
    let embed_chunks = chunk_embeds(embeds);

    for (index, chunk) in embed_chunks.iter().enumerate() {
        let mut content = format!(
            "**{}** - **New articles** ({} items)",
            feed_title,
            embeds.len()
        );
        if embed_chunks.len() > 1 {
            content = format!("{} [{}]", content, index + 1);
        }

        let embeds_payload: Vec<_> = chunk
            .iter()
            .map(|embed| {
                serde_json::json!({
                    "title": embed.title,
                    "url": embed.link,
                    "description": embed.summary,
                })
            })
            .collect();
        let payload = build_payload(content, embeds_payload);

        let response = match post_with_retry(&client, webhook_url, &payload).await {
            Ok(response) => response,
            Err(err) => {
                return Err(io::Error::other(format!(
                    "Skipping RSS feed {}: failed to notify webhook after 3 attempts: {}",
                    feed_url, err
                ))
                .into());
            }
        };

        if response.status().is_client_error() || response.status().is_server_error() {
            let status = response.status();
            let body = response.text().await.unwrap_or_else(|_| String::new());
            return Err(io::Error::other(format!(
                "Skipping RSS feed {}: webhook returned {}{}",
                feed_url,
                status,
                if body.is_empty() {
                    String::new()
                } else {
                    format!(": {}", body)
                }
            ))
            .into());
        }
    }

    let _ = articles;
    Ok(())
}

pub fn record_sent_articles(
    conn: &Connection,
    feed_id: u32,
    articles: &[Article<'_>],
) -> Result<(), rusqlite::Error> {
    let has_published = has_published_column(conn)?;
    let insert_query = if has_published {
        "INSERT OR IGNORE INTO rss_feed_articles (feed_id, url, title, published) VALUES (?, ?, ?, ?)"
    } else {
        "INSERT OR IGNORE INTO rss_feed_articles (feed_id, url, title) VALUES (?, ?, ?)"
    };

    for article in articles {
        if has_published {
            conn.execute(
                insert_query,
                params![feed_id, article.url, article.title, article.published],
            )?;
        } else {
            conn.execute(insert_query, params![feed_id, article.url, article.title])?;
        }
    }

    Ok(())
}

pub fn load_sent_article_urls(
    conn: &Connection,
    feed_id: u32,
) -> Result<std::collections::HashSet<String>, rusqlite::Error> {
    let mut stmt = conn.prepare("SELECT url FROM rss_feed_articles WHERE feed_id = ?")?;
    let rows = stmt.query_map(params![feed_id], |row| row.get::<_, String>(0))?;

    let mut urls = std::collections::HashSet::new();
    for row in rows {
        urls.insert(row?);
    }

    Ok(urls)
}
