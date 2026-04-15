use rusqlite::Connection;
use shiori_keeper_batch::{database_path, fetch_app_settings, fetch_rss_feeds};

use reqwest::Url;
use rss::Channel;
use std::error::Error;
use std::io;
mod webhook;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let conn = Connection::open(database_path())?;

    let rss_feeds = fetch_rss_feeds(&conn)?;
    let app_settings = fetch_app_settings(&conn)?;

    if rss_feeds.is_empty() {
        println!("No RSS feed data");
        return Ok(());
    }

    if app_settings.is_empty() {
        eprintln!("Not setting webhook URL");
        return Err(io::Error::other("Not setting webhook URL").into());
    }

    let webhook_url = &app_settings[0].value;

    for rss_feed in rss_feeds {
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
        let sent_urls = match webhook::load_sent_article_urls(&conn, rss_feed.id) {
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
            println!("No new articles found.");
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

        if let Err(err) = webhook::record_sent_articles(&conn, rss_feed.id, &articles) {
            eprintln!(
                "Skipping RSS feed {}: failed to record sent articles: {}",
                rss_feed.url, err
            );
            continue;
        }
    }
    Ok(())
}
