from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

from api.database import get_db
from api.model.models import (
    SettingsWebhookPingRequest,
    SettingsWebhookPingResponse,
    SettingsWebhookResponse,
    SettingsWebhookUpdate,
)
from api.repositories.settings_repo import SettingsRepository

WEBHOOK_SETTING_KEY = "default_webhook_url"


class SettingsService:
    def _validate_discord_webhook_url(self, webhook_url: str) -> None:
        parsed = urlparse(webhook_url)
        valid_hosts = {"discord.com", "www.discord.com", "discordapp.com", "www.discordapp.com"}
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in valid_hosts:
            raise HTTPException(status_code=422, detail="Webhook URL must be a Discord webhook URL")
        if not parsed.path.startswith("/api/webhooks/"):
            raise HTTPException(status_code=422, detail="Webhook URL must be a Discord webhook URL")

    def set_webhook(self, data: SettingsWebhookUpdate) -> SettingsWebhookResponse:
        with get_db() as conn:
            repo = SettingsRepository(conn)
            webhook_url = str(data.webhook_url)
            self._validate_discord_webhook_url(webhook_url)
            return SettingsWebhookResponse(webhook_url=repo.set(WEBHOOK_SETTING_KEY, webhook_url))

    def ping_webhook(self, data: SettingsWebhookPingRequest) -> SettingsWebhookPingResponse:
        webhook_url = str(data.webhook_url)
        self._validate_discord_webhook_url(webhook_url)

        try:
            response = httpx.post(
                webhook_url,
                json={"content": "ping"},
                timeout=5.0,
            )
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Failed to reach Discord webhook") from exc

        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="Failed to reach Discord webhook")

        return SettingsWebhookPingResponse(pong=True)

    def get_webhook(self) -> SettingsWebhookResponse:
        with get_db() as conn:
            repo = SettingsRepository(conn)
            webhook_url = repo.get(WEBHOOK_SETTING_KEY)
            if webhook_url is None:
                raise HTTPException(status_code=404, detail="Webhook URL is not configured")
            return SettingsWebhookResponse(webhook_url=webhook_url)
