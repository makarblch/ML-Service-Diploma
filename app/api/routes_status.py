from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.ml_job_state_repository import MlJobStateRepository
from app.schemas.status_response import JobStatusResponse, PredictionResultResponse

router = APIRouter(tags=["status"])


@router.get(
    "/jobs/{job_id}/status",
    response_model=JobStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
) -> JobStatusResponse:
    job_state_repo = MlJobStateRepository(db)
    job = job_state_repo.get_by_job_id(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    result = None

    if job.result_payload_json:
        result = PredictionResultResponse(**job.result_payload_json)

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        updated_at=job.updated_at,
        error_message=job.error_message,
        result=result,
    )
