from sqlalchemy.orm import Session

from app.repositories.ml_error_log_repository import MlErrorLogRepository
from app.repositories.ml_job_log_repository import MlJobLogRepository


class LoggingService:
    def __init__(self, db: Session) -> None:
        self.job_log_repo = MlJobLogRepository(db)
        self.error_log_repo = MlErrorLogRepository(db)

    def log_event(
        self,
        job_id: str,
        event_type: str,
        status: str,
        message: str | None = None,
        model_version: str | None = None,
    ) -> None:
        self.job_log_repo.create_log(
            job_id=job_id,
            event_type=event_type,
            status=status,
            message=message,
            model_version=model_version,
        )

    def log_error(
        self,
        error_stage: str,
        error_type: str,
        error_message: str,
        job_id: str | None = None,
        stacktrace: str | None = None,
    ) -> None:
        self.error_log_repo.create_error(
            job_id=job_id,
            error_stage=error_stage,
            error_type=error_type,
            error_message=error_message,
            stacktrace=stacktrace,
        )