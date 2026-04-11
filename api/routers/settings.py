from fastapi import APIRouter

from api.database import API_BASE_URL
from api.model.models_settings import ApiBaseUrlResponse

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=ApiBaseUrlResponse)
def get_settings():
    return ApiBaseUrlResponse(api_base_url=API_BASE_URL)
