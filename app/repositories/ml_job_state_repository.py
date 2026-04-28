from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import JobStatus
from app.db.models import MlJobState


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MlJobStateRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_job(
        self,
        job_id: str,
        status: str,
        callback_url: str | None,
        requested_payload_json: dict | None = None,
        model_version: str | None = None,
    ) -> MlJobState:
        job = MlJobState(
            job_id=job_id,
            status=status,
            callback_url=callback_url,
            requested_payload_json=requested_payload_json,
            model_version=model_version,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_job_id(self, job_id: str) -> MlJobState | None:
        stmt = select(MlJobState).where(MlJobState.job_id == job_id)
        return self.db.scalar(stmt)

    def update_status(
        self,
        job_id: str,
        status: str,
        error_message: str | None = None,
        result_payload_json: dict | None = None,
        model_version: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> MlJobState | None:
        job = self.get_by_job_id(job_id)
        if not job:
            return None

        job.status = status
        job.error_message = error_message
        job.updated_at = utc_now()

        if result_payload_json is not None:
            job.result_payload_json = result_payload_json
        if model_version is not None:
            job.model_version = model_version
        if started_at is not None:
            job.started_at = started_at
        if completed_at is not None:
            job.completed_at = completed_at

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def claim_next_pending_job(self) -> MlJobState | None:
        """Атомарно забирает следующую pending-задачу и переводит её в running."""
        with self.db.begin():
            stmt = (
                select(MlJobState)
                .where(MlJobState.status == JobStatus.pending.value)
                .order_by(MlJobState.created_at.asc())
                .with_for_update(skip_locked=True)
                .limit(1)
            )

            job = self.db.execute(stmt).scalar_one_or_none()
            if job is None:
                return None

            now = utc_now()
            job.status = JobStatus.running.value
            job.started_at = now
            job.updated_at = now

            self.db.add(job)

        self.db.refresh(job)
        return job