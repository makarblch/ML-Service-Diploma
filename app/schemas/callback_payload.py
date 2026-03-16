from datetime import datetime
from typing import Optional

from pydantic import Field

from app.core.enums import JobStatus
from app.schemas.common import BaseSchema


class CallbackResult(BaseSchema):
    predicted_turnover: float = Field(..., ge=0)


class CallbackModelInfo(BaseSchema):
    model_version: str = Field(..., min_length=1, max_length=64)


class PredictionCallbackPayload(BaseSchema):
    job_id: str = Field(..., min_length=1, max_length=64)
    status: JobStatus
    result: Optional[CallbackResult] = None
    model_info: Optional[CallbackModelInfo] = None
    error_message: Optional[str] = None
    completed_at: datetime