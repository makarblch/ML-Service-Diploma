from pydantic import Field

from app.core.enums import JobStatus
from app.schemas.common import BaseSchema


class PredictJobAcceptedResponse(BaseSchema):
    job_id: str = Field(..., min_length=1, max_length=64)
    status: JobStatus
    message: str