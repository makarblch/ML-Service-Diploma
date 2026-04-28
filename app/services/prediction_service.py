from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.enums import ErrorStage, JobEventType, JobStatus
from app.ml.model_loader import ModelLoader
from app.ml.schema_loader import SchemaLoader
from app.repositories.ml_job_state_repository import MlJobStateRepository
from app.repositories.model_registry_repository import ModelRegistryRepository
from app.services.logging_service import LoggingService
from app.services.prediction_input_builder import PredictionInputBuilder


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PredictionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.job_state_repo = MlJobStateRepository(db)
        self.model_registry_repo = ModelRegistryRepository(db)
        self.logging_service = LoggingService(db)

    def run_prediction(
        self,
        job_id: str,
        features: dict,
        requested_model_version: Optional[str] = None,
    ) -> dict:
        job_state = self.job_state_repo.get_by_job_id(job_id)
        if not job_state:
            raise ValueError(f"Job {job_id} not found")

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

            pipeline = ModelLoader.load_model(model_record.artifact_path)
            feature_schema = SchemaLoader.load_schema(model_record.feature_schema_path)

            required_features = feature_schema["required_features"]
            feature_order = feature_schema["feature_order"]

            missing = [f for f in required_features if f not in features]
            if missing:
                raise ValueError(f"Missing required features: {missing}")

            input_df = PredictionInputBuilder.build_dataframe(
                features=features,
                feature_order=feature_order,
            )

            prediction = pipeline.predict(input_df)
            raw_predicted_turnover = float(prediction[0])
            predicted_turnover = max(0.0, raw_predicted_turnover)

            result_payload = {
                "predicted_turnover": predicted_turnover,
                "model_version": model_version,
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