import logging
import time

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.repositories.ml_job_state_repository import MlJobStateRepository
from app.services.prediction_service import PredictionService

POLL_INTERVAL_SECONDS = 2

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def process_one_job(db: Session) -> bool:
    job_repo = MlJobStateRepository(db)
    prediction_service = PredictionService(db)

    job = job_repo.claim_next_pending_job()
    if job is None:
        return False

    logger.info("Claimed job %s", job.job_id)

    payload = job.requested_payload_json or {}
    features_model = payload.get("features")
    requested_model_version = payload.get("model_version")

    if not features_model:
        raise ValueError(f"Job {job.job_id} does not contain features in requested_payload_json")

    prediction_service.run_prediction(
        job_id=job.job_id,
        features=features_model,
        requested_model_version=requested_model_version,
    )

    logger.info("Finished job %s", job.job_id)
    return True


def run_worker() -> None:
    logger.info("Prediction worker started")

    while True:
        db = SessionLocal()
        try:
            processed = process_one_job(db)
            if not processed:
                time.sleep(POLL_INTERVAL_SECONDS)
        except Exception as exc:
            logger.exception("Worker iteration failed: %s", exc)
            time.sleep(POLL_INTERVAL_SECONDS)
        finally:
            db.close()


if __name__ == "__main__":
    run_worker()