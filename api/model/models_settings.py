from pydantic import BaseModel


class ApiBaseUrlResponse(BaseModel):
    api_base_url: str
