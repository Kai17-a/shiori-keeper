from fastapi import APIRouter

from api.database import get_db
from api.model.models_settings import ApiBaseUrlResponse, ApiBaseUrlUpdate
from api.repositories.settings_repo import SettingsRepository

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=ApiBaseUrlResponse)
def get_settings():
    with get_db() as conn:
        repo = SettingsRepository(conn)
        return ApiBaseUrlResponse(api_base_url=repo.get_api_base_url())


@router.patch("", response_model=ApiBaseUrlResponse)
def update_settings(body: ApiBaseUrlUpdate):
    with get_db() as conn:
        repo = SettingsRepository(conn)
        value = repo.set_api_base_url(str(body.api_base_url))
        return ApiBaseUrlResponse(api_base_url=value)
