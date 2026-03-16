from sqlalchemy.orm import Session

from app.db.models import MlJobLog


class MlJobLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_log(
        self,
        job_id: str,
        event_type: str,
        status: str,
        message: str | None = None,
        model_version: str | None = None,
    ) -> MlJobLog:
        log = MlJobLog(
            job_id=job_id,
            event_type=event_type,
            status=status,
            message=message,
            model_version=model_version,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log