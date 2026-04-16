from fastapi import APIRouter, Depends

from api.dependencies import get_settings_service
from api.model.models import (
    SettingsRssExecutionResponse,
    SettingsRssExecutionUpdate,
    SettingsWebhookPingRequest,
    SettingsWebhookPingResponse,
    SettingsWebhookResponse,
    SettingsWebhookUpdate,
)
from api.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.put("/webhook", status_code=200, response_model=SettingsWebhookResponse)
def set_webhook(
    body: SettingsWebhookUpdate,
    service: SettingsService = Depends(get_settings_service),
):
    return service.set_webhook(body)


@router.post(
    "/webhook/ping", status_code=200, response_model=SettingsWebhookPingResponse
)
def ping_webhook(
    body: SettingsWebhookPingRequest,
    service: SettingsService = Depends(get_settings_service),
):
    return service.ping_webhook(body)


@router.get("/webhook", status_code=200, response_model=SettingsWebhookResponse)
def get_webhook(service: SettingsService = Depends(get_settings_service)):
    return service.get_webhook()


@router.get(
    "/rss-execution", status_code=200, response_model=SettingsRssExecutionResponse
)
def get_rss_execution(service: SettingsService = Depends(get_settings_service)):
    return service.get_rss_execution()


@router.put(
    "/rss-execution", status_code=200, response_model=SettingsRssExecutionResponse
)
def set_rss_execution(
    body: SettingsRssExecutionUpdate,
    service: SettingsService = Depends(get_settings_service),
):
    return service.set_rss_execution(body)
