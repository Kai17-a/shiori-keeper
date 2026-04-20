use reqwest::Url;
use rss::Channel;
use rusqlite::Connection;
use std::collections::HashSet;
use std::error::Error;

use crate::{
    fetch_app_settings, fetch_rss_feeds, rss_periodic_execution_enabled,
    rss_webhook_notification_enabled, webhook,
};

pub async fn run_batch(conn: &Connection) -> Result<(), Box<dyn Error>> {
    let rss_feeds = fetch_rss_feeds(conn)?;
    let rss_enabled = rss_periodic_execution_enabled(conn)?;

    if rss_feeds.is_empty() {
        return Ok(());
    }

    if !rss_enabled {
        return Ok(());
    }

    if !rss_webhook_notification_enabled(conn)? {
        return Ok(());
    }

    let app_settings = fetch_app_settings(conn)?;
    if app_settings.is_empty() {
        eprintln!("Not setting webhook URL");
        return Ok(());
    }

    let webhook_url = &app_settings[0].value;

    for rss_feed in rss_feeds {
        if rss_feed.notify_webhook_enabled == 0 {
            continue;
        }
        let url = match Url::parse(&rss_feed.url) {
            Ok(url) => url,
            Err(err) => {
                eprintln!("Skipping invalid RSS URL {}: {}", rss_feed.url, err);
                continue;
            }
        };
        let content = match reqwest::get(url).await {
            Ok(response) => match response.bytes().await {
                Ok(content) => content,
                Err(err) => {
                    eprintln!(
                        "Skipping RSS feed {}: failed to read body: {}",
                        rss_feed.url, err
                    );
                    continue;
                }
            },
            Err(err) => {
                eprintln!(
                    "Skipping RSS feed {}: request failed: {}",
                    rss_feed.url, err
                );
                continue;
            }
        };
        let channel = match Channel::read_from(&content[..]) {
            Ok(channel) => channel,
            Err(err) => {
                eprintln!(
                    "Skipping RSS feed {}: failed to parse channel: {}",
                    rss_feed.url, err
                );
                continue;
            }
        };
        let sent_urls: HashSet<String> = match webhook::load_sent_article_urls(conn, rss_feed.id) {
            Ok(urls) => urls,
            Err(err) => {
                eprintln!(
                    "Skipping RSS feed {}: failed to load sent articles: {}",
                    rss_feed.url, err
                );
                continue;
            }
        };

        let mut articles = Vec::new();
        let mut embeds = Vec::new();
        for item in channel.items() {
            let title = item.title().unwrap_or("(no title)");
            let link = item.link().unwrap_or("(no link)");
            if sent_urls.contains(link) {
                continue;
            }
            let published = item.pub_date().unwrap_or("(no published date)");
            let summary = item
                .description()
                .or(item.content())
                .unwrap_or("(no summary)");

            embeds.push(webhook::Embed {
                title,
                link,
                published,
                summary,
            });
            articles.push(webhook::Article {
                url: link,
                title,
                published,
            });
        }

        if embeds.is_empty() {
            continue;
        }

        if let Err(err) = webhook::send_rss_webhook(
            webhook_url,
            &rss_feed.title,
            &rss_feed.url,
            &embeds,
            &articles,
        )
        .await
        {
            eprintln!("{}", err);
            continue;
        }

        if let Err(err) = webhook::record_sent_articles(conn, rss_feed.id, &articles) {
            eprintln!(
                "Skipping RSS feed {}: failed to record sent articles: {}",
                rss_feed.url, err
            );
            continue;
        }
    }
    Ok(())
}
