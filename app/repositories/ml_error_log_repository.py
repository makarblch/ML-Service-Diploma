from sqlalchemy.orm import Session

from app.db.models import MlErrorLog


class MlErrorLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_error(
        self,
        error_stage: str,
        error_type: str,
        error_message: str,
        job_id: str | None = None,
        stacktrace: str | None = None,
    ) -> MlErrorLog:
        error = MlErrorLog(
            job_id=job_id,
            error_stage=error_stage,
            error_type=error_type,
            error_message=error_message,
            stacktrace=stacktrace,
        )
        self.db.add(error)
        self.db.commit()
        self.db.refresh(error)
        return error