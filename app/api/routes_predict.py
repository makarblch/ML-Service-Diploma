from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from psycopg.errors import UniqueViolation

from app.core.enums import JobEventType, JobStatus
from app.db.session import get_db
from app.repositories.ml_job_state_repository import MlJobStateRepository
from app.repositories.model_registry_repository import ModelRegistryRepository
from app.schemas.predict_request import PredictJobRequest
from app.schemas.predict_response import PredictJobAcceptedResponse
from app.services.logging_service import LoggingService

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
    model_registry_repo = ModelRegistryRepository(db)
    logging_service = LoggingService(db)

    if payload.model_version and payload.model_version != "latest":
        model_record = model_registry_repo.get_model_by_version(payload.model_version)
        if model_record is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Model version '{payload.model_version}' not found in model_registry",
            )

    try:
        job_state_repo.create_job(
            job_id=payload.job_id,
            status=JobStatus.pending.value,
            callback_url=str(payload.callback_url) if payload.callback_url else None,
            requested_payload_json=payload.model_dump(mode="json"),
            model_version=payload.model_version,
        )
    except IntegrityError as exc:
        db.rollback()

        if isinstance(exc.orig, UniqueViolation):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Job with job_id='{payload.job_id}' already exists",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {str(exc.orig)}",
        )

    logging_service.log_event(
        job_id=payload.job_id,
        event_type=JobEventType.job_received.value,
        status=JobStatus.pending.value,
        message="Prediction job accepted by Python ML service",
        model_version=payload.model_version,
    )

    return PredictJobAcceptedResponse(
        job_id=payload.job_id,
        status=JobStatus.pending,
        message="Prediction job accepted",
    )