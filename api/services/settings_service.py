import httpx
from fastapi import HTTPException

from api.database import get_db
from api.model.models import (
    SettingsRssExecutionResponse,
    SettingsRssExecutionUpdate,
    SettingsWebhookPingRequest,
    SettingsWebhookPingResponse,
    SettingsWebhookResponse,
    SettingsWebhookUpdate,
)
from api.repositories.settings_repo import SettingsRepository
from api.services.webhook_service import (
    build_webhook_payload,
    detect_webhook_service,
    send_webhook,
)

WEBHOOK_SETTING_KEY = "default_webhook_url"
RSS_EXECUTION_SETTING_KEY = "rss_periodic_execution_enabled"


class SettingsService:
    def _validate_webhook_url(self, webhook_url: str) -> None:
        from urllib.parse import urlparse

        parsed = urlparse(webhook_url)
        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(
                status_code=422, detail="Webhook URL must be a valid URL"
            )

    def set_webhook(self, data: SettingsWebhookUpdate) -> SettingsWebhookResponse:
        with get_db() as conn:
            repo = SettingsRepository(conn)
            webhook_url = str(data.webhook_url)
            self._validate_webhook_url(webhook_url)
            detect_webhook_service(webhook_url)
            return SettingsWebhookResponse(
                webhook_url=repo.set(WEBHOOK_SETTING_KEY, webhook_url)
            )

    def ping_webhook(
        self, data: SettingsWebhookPingRequest
    ) -> SettingsWebhookPingResponse:
        webhook_url = str(data.webhook_url)
        self._validate_webhook_url(webhook_url)
        webhook_service = detect_webhook_service(webhook_url)

        try:
            response = send_webhook(
                webhook_url,
                build_webhook_payload(webhook_service, content="ping"),
            )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Failed to reach Microsoft Teams webhook"
                    if webhook_service == "teams"
                    else "Failed to reach Discord webhook"
                ),
            ) from exc

        if response.status_code >= 400:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Failed to reach Microsoft Teams webhook"
                    if webhook_service == "teams"
                    else "Failed to reach Discord webhook"
                ),
            )

        return SettingsWebhookPingResponse(pong=True)

    def get_webhook(self) -> SettingsWebhookResponse:
        with get_db() as conn:
            repo = SettingsRepository(conn)
            webhook_url = repo.get(WEBHOOK_SETTING_KEY)
            if webhook_url is None:
                raise HTTPException(
                    status_code=404, detail="Webhook URL is not configured"
                )
            return SettingsWebhookResponse(webhook_url=webhook_url)

    def get_rss_execution(self) -> SettingsRssExecutionResponse:
        with get_db() as conn:
            repo = SettingsRepository(conn)
            return SettingsRssExecutionResponse(
                enabled=repo.get_bool(RSS_EXECUTION_SETTING_KEY)
            )

    def set_rss_execution(
        self, data: SettingsRssExecutionUpdate
    ) -> SettingsRssExecutionResponse:
        with get_db() as conn:
            repo = SettingsRepository(conn)
            return SettingsRssExecutionResponse(
                enabled=repo.set_bool(RSS_EXECUTION_SETTING_KEY, data.enabled)
            )
