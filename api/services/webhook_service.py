from __future__ import annotations

from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

DISCORD_WEBHOOK_ERROR_DETAIL = "Failed to notify Discord webhook"
TEAMS_WEBHOOK_ERROR_DETAIL = "Failed to notify Microsoft Teams webhook"


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

    teams_hosts = {"outlook.office.com", "www.outlook.office.com"}
    if parsed.scheme in {"http", "https"} and (
        hostname in teams_hosts or hostname.endswith(".webhook.office.com")
    ):
        if path.startswith("/webhook") or "/IncomingWebhook/" in path:
            return "teams"

    raise HTTPException(
        status_code=422,
        detail="Webhook URL must be a Discord or Microsoft Teams webhook URL",
    )


def build_webhook_payload(webhook_service: str, *, content: str) -> dict[str, object]:
    if webhook_service == "discord":
        return {"username": "Shiori Keeper", "content": content}
    if webhook_service == "teams":
        return {
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": content,
                                "wrap": True,
                            }
                        ],
                    },
                }
            ]
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

    if webhook_service == "teams":
        body: list[dict[str, object]] = [
            {
                "type": "TextBlock",
                "text": f"{feed_title} - 新着ニュース",
                "weight": "Bolder",
                "size": "Medium",
                "wrap": True,
            }
        ]
        for article in articles:
            body.append(
                {
                    "type": "TextBlock",
                    "text": f"- [{article['title']}]({article['url']})",
                    "wrap": True,
                    "markdown": True,
                }
            )
        return {
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": body,
                    },
                }
            ]
        }

    raise ValueError(f"Unsupported webhook service: {webhook_service}")


def send_webhook(webhook_url: str, payload: dict[str, object]) -> httpx.Response:
    return httpx.post(webhook_url, json=payload, timeout=5.0)
