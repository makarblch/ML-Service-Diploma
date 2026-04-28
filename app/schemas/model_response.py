from datetime import datetime

from pydantic import Field

from app.schemas.common import BaseSchema


class ModelInfoResponse(BaseSchema):
    model_version: str = Field(..., min_length=1, max_length=64)
    model_name: str | None = None
    is_active: bool
    description: str | None = None
    created_at: datetime


class ModelListResponse(BaseSchema):
    models: list[ModelInfoResponse]