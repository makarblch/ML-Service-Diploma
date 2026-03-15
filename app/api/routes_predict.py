from datetime import datetime, timezone

from fastapi import APIRouter, status

from app.core.enums import JobStatus
from app.schemas.predict_request import PredictJobRequest
from app.schemas.predict_response import PredictJobAcceptedResponse

router = APIRouter(tags=["prediction"])

# Временное хранилище для MVP, позже заменим на БД
JOB_STORE: dict[str, dict] = {}


@router.post(
    "/jobs/predict",
    response_model=PredictJobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_prediction_job(payload: PredictJobRequest) -> PredictJobAcceptedResponse:
    JOB_STORE[payload.job_id] = {
        "status": JobStatus.pending,
        "updated_at": datetime.now(timezone.utc),
    }

    return PredictJobAcceptedResponse(
        job_id=payload.job_id,
        status=JobStatus.pending,
        message="Prediction job accepted",
    )