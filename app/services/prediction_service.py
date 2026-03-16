from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.core.enums import JobEventType, JobStatus, ErrorStage
from app.repositories.ml_job_state_repository import MlJobStateRepository
from app.repositories.model_registry_repository import ModelRegistryRepository
from app.services.logging_service import LoggingService
from app.services.callback_service import CallbackService
from app.ml.model_loader import ModelLoader
from app.schemas.callback_payload import (
    CallbackModelInfo,
    CallbackResult,
    PredictionCallbackPayload,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PredictionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.job_state_repo = MlJobStateRepository(db)
        self.model_registry_repo = ModelRegistryRepository(db)
        self.logging_service = LoggingService(db)
        self.callback_service = CallbackService()

    def run_prediction(
        self,
        job_id: str,
        features: dict,
        requested_model_version: Optional[str] = None,
    ) -> dict:
        job_state = self.job_state_repo.get_by_job_id(job_id)
        if not job_state:
            raise ValueError(f"Job {job_id} not found")

        callback_url = job_state.callback_url

        try:
            self.logging_service.log_event(
                job_id=job_id,
                event_type=JobEventType.model_lookup_started.value,
                status=JobStatus.running.value,
                message="Starting model lookup",
            )

            model_record = self._resolve_model(requested_model_version)
            model_version = model_record.model_version

            self.job_state_repo.update_status(
                job_id=job_id,
                status=JobStatus.running.value,
                model_version=model_version,
                started_at=utc_now(),
            )

            self.logging_service.log_event(
                job_id=job_id,
                event_type=JobEventType.model_loaded.value,
                status=JobStatus.running.value,
                message=f"Loaded model version {model_version}",
                model_version=model_version,
            )

            self.logging_service.log_event(
                job_id=job_id,
                event_type=JobEventType.inference_started.value,
                status=JobStatus.running.value,
                message="Inference started",
                model_version=model_version,
            )

            model = ModelLoader.get_model(model_version)
            predicted_turnover = model.predict(features)

            result_payload = {
                "predicted_turnover": predicted_turnover
            }

            completed_at = utc_now()

            self.job_state_repo.update_status(
                job_id=job_id,
                status=JobStatus.completed.value,
                result_payload_json=result_payload,
                model_version=model_version,
                completed_at=completed_at,
            )

            self.logging_service.log_event(
                job_id=job_id,
                event_type=JobEventType.inference_completed.value,
                status=JobStatus.completed.value,
                message="Inference completed successfully",
                model_version=model_version,
            )

            self.logging_service.log_event(
                job_id=job_id,
                event_type=JobEventType.callback_started.value,
                status=JobStatus.completed.value,
                message="Sending callback to Kotlin service",
                model_version=model_version,
            )

            callback_payload = PredictionCallbackPayload(
                job_id=job_id,
                status=JobStatus.completed,
                result=CallbackResult(predicted_turnover=predicted_turnover),
                model_info=CallbackModelInfo(model_version=model_version),
                completed_at=completed_at,
            )

            self.callback_service.send_prediction_callback(
                callback_url=callback_url,
                payload=callback_payload,
            )

            self.logging_service.log_event(
                job_id=job_id,
                event_type=JobEventType.callback_sent.value,
                status=JobStatus.completed.value,
                message="Callback delivered successfully",
                model_version=model_version,
            )

            return {
                "job_id": job_id,
                "status": JobStatus.completed.value,
                "result": result_payload,
                "model_version": model_version,
            }

        except Exception as exc:
            completed_at = utc_now()

            self.job_state_repo.update_status(
                job_id=job_id,
                status=JobStatus.failed.value,
                error_message=str(exc),
                completed_at=completed_at,
            )

            self.logging_service.log_event(
                job_id=job_id,
                event_type=JobEventType.job_failed.value,
                status=JobStatus.failed.value,
                message=str(exc),
            )

            self.logging_service.log_error(
                job_id=job_id,
                error_stage=ErrorStage.inference.value,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )

            # Пробуем отправить callback об ошибке
            try:
                error_callback_payload = PredictionCallbackPayload(
                    job_id=job_id,
                    status=JobStatus.failed,
                    error_message=str(exc),
                    completed_at=completed_at,
                )

                self.callback_service.send_prediction_callback(
                    callback_url=callback_url,
                    payload=error_callback_payload,
                )

                self.logging_service.log_event(
                    job_id=job_id,
                    event_type=JobEventType.callback_sent.value,
                    status=JobStatus.failed.value,
                    message="Failure callback delivered successfully",
                )
            except Exception as callback_exc:
                self.logging_service.log_event(
                    job_id=job_id,
                    event_type=JobEventType.callback_failed.value,
                    status=JobStatus.failed.value,
                    message=str(callback_exc),
                )

                self.logging_service.log_error(
                    job_id=job_id,
                    error_stage=ErrorStage.callback.value,
                    error_type=type(callback_exc).__name__,
                    error_message=str(callback_exc),
                )

            raise

    def _resolve_model(self, requested_model_version: Optional[str] = None):
        if requested_model_version and requested_model_version != "latest":
            model_record = self.model_registry_repo.get_model_by_version(
                requested_model_version
            )
        else:
            model_record = self.model_registry_repo.get_active_model()

        if not model_record:
            raise ValueError("Model version not found in model_registry")

        return model_record