from sqlalchemy import select

from app.db.models import ModelRegistry
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(
            select(ModelRegistry).where(ModelRegistry.model_version == "v1.0.0")
        )
        if existing:
            print("Model version v1.0.0 already exists.")
            return

        model = ModelRegistry(
            model_version="v1.0.0",
            model_name="turnover_regression_model",
            artifact_path="artifacts/models/turnover_model_v1.0.0.joblib",
            preprocessor_path="artifacts/preprocessors/preprocessor_v1.0.0.joblib",
            feature_schema_path="artifacts/schemas/feature_schema_v1.0.0.json",
            is_active=True,
            description="Initial active model version for MVP inference flow.",
        )
        db.add(model)
        db.commit()
        print("Seeded model_registry with v1.0.0")
    finally:
        db.close()


if __name__ == "__main__":
    main()