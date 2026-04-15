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
    pub created_at: String,
    pub updated_at: String,
}

pub fn fetch_app_settings(conn: &Connection) -> Result<Vec<AppSetting>> {
    let mut stmt =
        conn.prepare("SELECT value FROM app_settings where key = 'default_webhook_url'")?;
    let app_settings_iter = stmt.query_map([], |row| Ok(AppSetting { value: row.get(0)? }))?;

    app_settings_iter.collect()
}

pub fn fetch_rss_feeds(conn: &Connection) -> Result<Vec<RSSFeed>> {
    let mut stmt = conn.prepare("SELECT * FROM rss_feeds")?;
    let rss_feed_iter = stmt.query_map([], |row| {
        Ok(RSSFeed {
            id: row.get(0)?,
            url: row.get(1)?,
            title: row.get(2)?,
            description: row.get(3)?,
            created_at: row.get(4)?,
            updated_at: row.get(5)?,
        })
    })?;

    rss_feed_iter.collect()
}
