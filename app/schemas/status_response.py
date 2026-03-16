from datetime import datetime
from pydantic import Field

from app.core.enums import JobStatus
from app.schemas.common import BaseSchema


class JobStatusResponse(BaseSchema):
    job_id: str = Field(..., min_length=1, max_length=64)
    status: JobStatus
    updated_at: datetime