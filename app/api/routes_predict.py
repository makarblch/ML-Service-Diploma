from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.enums import JobEventType, JobStatus
from app.db.session import get_db
from app.repositories.ml_job_state_repository import MlJobStateRepository
from app.schemas.predict_request import PredictJobRequest
from app.schemas.predict_response import PredictJobAcceptedResponse
from app.services.logging_service import LoggingService
from app.services.prediction_service import PredictionService

router = APIRouter(tags=["prediction"])


@router.post(
    "/jobs/predict",
    response_model=PredictJobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_prediction_job(
    payload: PredictJobRequest,
    db: Session = Depends(get_db),
) -> PredictJobAcceptedResponse:
    job_state_repo = MlJobStateRepository(db)
    logging_service = LoggingService(db)

    job_state_repo.create_job(
        job_id=payload.job_id,
        status=JobStatus.pending.value,
        callback_url=str(payload.callback_url),
        requested_payload_json=payload.model_dump(mode="json"),
        model_version=payload.model_version,
    )

    logging_service.log_event(
        job_id=payload.job_id,
        event_type=JobEventType.job_received.value,
        status=JobStatus.pending.value,
        message="Prediction job accepted by Python ML service",
        model_version=payload.model_version,
    )

    prediction_service = PredictionService(db)
    prediction_service.run_prediction(
        job_id=payload.job_id,
        features=payload.features.model_dump(),
        requested_model_version=payload.model_version,
    )

    return PredictJobAcceptedResponse(
        job_id=payload.job_id,
        status=JobStatus.pending,
        message="Prediction job accepted",
    )