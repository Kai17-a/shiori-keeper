from __future__ import annotations

from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

def detect_webhook_service(webhook_url: str) -> str:
    parsed = urlparse(webhook_url)
    hostname = parsed.hostname or ""
    path = parsed.path

    discord_hosts = {
        "discord.com",
        "www.discord.com",
        "discordapp.com",
        "www.discordapp.com",
    }
    if parsed.scheme in {"http", "https"} and hostname in discord_hosts and path.startswith(
        "/api/webhooks/"
    ):
        return "discord"

    if (
        parsed.scheme in {"http", "https"}
        and hostname == "hooks.slack.com"
        and path.startswith("/services/")
    ):
        parts = [part for part in path.split("/") if part]
        if len(parts) == 4 and parts[0] == "services":
            return "slack"

    raise HTTPException(
        status_code=422,
        detail="Webhook URL must be a Discord or Slack webhook URL",
    )


def build_webhook_payload(webhook_service: str, *, content: str) -> dict[str, object]:
    if webhook_service == "discord":
        return {"username": "Shiori Keeper", "content": content}
    if webhook_service == "slack":
        return {
            "username": "Shiori Keeper",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": content,
                    },
                }
            ],
        }
    raise ValueError(f"Unsupported webhook service: {webhook_service}")


def build_rss_notification_payload(
    webhook_service: str,
    *,
    feed_title: str,
    articles: list[dict[str, object]],
    total_articles: int | None = None,
    chunk_index: int = 1,
    chunk_count: int = 1,
) -> dict[str, object]:
    if webhook_service == "discord":
        article_count = total_articles if total_articles is not None else len(articles)
        embeds = [
            {
                "title": str(article["title"]),
                "url": str(article["url"]),
                **(
                    {"description": str(article["summary"])}
                    if article.get("summary")
                    else {}
                ),
            }
            for article in articles
        ]
        content = f"**{feed_title}** - **New articles** ({article_count} items)"
        if chunk_count > 1:
            content = f"{content} [{chunk_index}]"
        return {"username": "Shiori Keeper", "content": content, "embeds": embeds}

    if webhook_service == "slack":
        article_count = total_articles if total_articles is not None else len(articles)
        header_text = f"📰 {feed_title} - 新着ニュース ({article_count}件)"
        if chunk_count > 1:
            header_text = f"{header_text} [{chunk_index}]"
        blocks: list[dict[str, object]] = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header_text,
                },
            }
        ]
        for article in articles:
            title = str(article["title"])
            url = str(article["url"])
            summary = article.get("summary")
            text = f"• <{url}|{title}>"
            if summary:
                text = f"{text}\n{str(summary)}"
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": text,
                    },
                }
            )
        return {"username": "Shiori Keeper", "blocks": blocks}

    raise ValueError(f"Unsupported webhook service: {webhook_service}")


def send_webhook(webhook_url: str, payload: dict[str, object]) -> httpx.Response:
    return httpx.post(webhook_url, json=payload, timeout=5.0)
