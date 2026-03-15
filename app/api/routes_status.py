from fastapi import APIRouter, HTTPException, status

from app.api.routes_predict import JOB_STORE
from app.schemas.status_response import JobStatusResponse

router = APIRouter(tags=["status"])


@router.get(
    "/jobs/{job_id}/status",
    response_model=JobStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def get_job_status(job_id: str) -> JobStatusResponse:
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        updated_at=job["updated_at"],
    )