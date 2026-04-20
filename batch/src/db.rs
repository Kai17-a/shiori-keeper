use rusqlite::{Connection, Result};
use std::env;

pub fn database_path() -> String {
    env::var("DATABASE_URL").unwrap_or_else(|_| "data/data.db".to_string())
}

#[derive(Debug)]
pub struct AppSetting {
    pub value: String,
}

#[derive(Debug)]
pub struct RSSFeed {
    pub id: u32,
    pub url: String,
    pub title: String,
    pub description: Option<String>,
    pub notify_webhook_enabled: i64,
    pub created_at: String,
    pub updated_at: String,
}

fn has_column(conn: &Connection, table: &str, column: &str) -> Result<bool> {
    let mut stmt = conn.prepare(&format!("PRAGMA table_info({})", table))?;
    let rows = stmt.query_map([], |row| Ok(row.get::<_, String>(1)?))?;
    for row in rows {
        if row? == column {
            return Ok(true);
        }
    }
    Ok(false)
}

pub fn fetch_app_settings(conn: &Connection) -> Result<Vec<AppSetting>> {
    let mut stmt =
        conn.prepare("SELECT value FROM app_settings where key = 'default_webhook_url'")?;
    let app_settings_iter = stmt.query_map([], |row| Ok(AppSetting { value: row.get(0)? }))?;

    app_settings_iter.collect()
}

pub fn rss_periodic_execution_enabled(conn: &Connection) -> Result<bool> {
    let mut stmt = conn.prepare(
        "SELECT rss_periodic_execution_enabled FROM app_settings WHERE key = 'rss_periodic_execution_enabled'",
    )?;
    let value = stmt.query_row([], |row| row.get::<_, i64>(0)).unwrap_or(0);
    Ok(value != 0)
}

pub fn rss_webhook_notification_enabled(conn: &Connection) -> Result<bool> {
    let mut stmt = conn.prepare(
        "SELECT rss_periodic_execution_enabled FROM app_settings WHERE key = 'rss_webhook_notification_enabled'",
    )?;
    let value = stmt.query_row([], |row| row.get::<_, i64>(0)).unwrap_or(0);
    Ok(value != 0)
}

pub fn fetch_rss_feeds(conn: &Connection) -> Result<Vec<RSSFeed>> {
    let has_notify_webhook_enabled = has_column(conn, "rss_feeds", "notify_webhook_enabled")?;
    let query = if has_notify_webhook_enabled {
        "SELECT id, url, title, description, notify_webhook_enabled, created_at, updated_at FROM rss_feeds WHERE notify_webhook_enabled = 1"
    } else {
        "SELECT id, url, title, description, 1 AS notify_webhook_enabled, created_at, updated_at FROM rss_feeds"
    };
    let mut stmt = conn.prepare(query)?;
    let rss_feed_iter = stmt.query_map([], |row| {
        Ok(RSSFeed {
            id: row.get(0)?,
            url: row.get(1)?,
            title: row.get(2)?,
            description: row.get(3)?,
            notify_webhook_enabled: row.get(4)?,
            created_at: row.get(5)?,
            updated_at: row.get(6)?,
        })
    })?;

    rss_feed_iter.collect()
}
