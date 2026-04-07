from pydantic import BaseModel, HttpUrl


class ApiBaseUrlResponse(BaseModel):
    api_base_url: str


class ApiBaseUrlUpdate(BaseModel):
    api_base_url: HttpUrl
