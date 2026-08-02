use reqwest::Url;
use rss::Channel;
use rusqlite::Connection;
use std::collections::HashSet;
use std::error::Error;
use std::time::Duration;

use crate::{
    fetch_rss_feeds, fetch_webhook_endpoints, rss_periodic_execution_enabled,
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

    let webhook_endpoints = fetch_webhook_endpoints(conn)?;
    if webhook_endpoints.is_empty() {
        eprintln!("Not setting webhook URL");
        return Ok(());
    }

    let http_client = reqwest::Client::builder()
        .timeout(Duration::from_secs(10))
        .build()?;

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
        let content = match http_client.get(url).send().await {
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

        let targets: Vec<&crate::WebhookEndpoint> = if rss_feed.webhook_ids.is_empty() {
            webhook_endpoints.iter().collect()
        } else {
            webhook_endpoints
                .iter()
                .filter(|endpoint| rss_feed.webhook_ids.contains(&endpoint.id))
                .collect()
        };
        if targets.is_empty() {
            eprintln!(
                "Skipping RSS feed {}: no matching webhook endpoints",
                rss_feed.url
            );
            continue;
        }

        let mut delivered = false;
        for endpoint in targets {
            if let Err(err) = webhook::send_rss_webhook(
                &endpoint.url,
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
            delivered = true;
        }

        if !delivered {
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
