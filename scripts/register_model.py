import argparse

from sqlalchemy import update, select

from app.db.models import ModelRegistry
from app.db.session import SessionLocal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register ML model in model_registry")

    parser.add_argument("--model-version", required=True, help="Unique model version, e.g. v1.1.0")
    parser.add_argument("--model-name", required=True, help="Human-readable model name")
    parser.add_argument("--artifact-path", required=True, help="Path to model artifact (.pkl/.joblib)")
    parser.add_argument(
        "--preprocessor-path",
        required=False,
        default="",
        help="Path to preprocessor artifact. For full pipeline can be same as artifact-path or empty.",
    )
    parser.add_argument(
        "--feature-schema-path",
        required=True,
        help="Path to feature schema json",
    )
    parser.add_argument(
        "--description",
        required=False,
        default=None,
        help="Optional model description",
    )
    parser.add_argument(
        "--activate",
        action="store_true",
        help="Make this model active",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    db = SessionLocal()
    try:
        existing = db.scalar(
            select(ModelRegistry).where(ModelRegistry.model_version == args.model_version)
        )
        if existing:
            raise ValueError(f"Model version {args.model_version} already exists")

        if args.activate:
            db.execute(update(ModelRegistry).values(is_active=False))

        model = ModelRegistry(
            model_version=args.model_version,
            model_name=args.model_name,
            artifact_path=args.artifact_path,
            preprocessor_path=args.preprocessor_path or args.artifact_path,
            feature_schema_path=args.feature_schema_path,
            is_active=args.activate,
            description=args.description,
        )

        db.add(model)
        db.commit()

        print(f"Model {args.model_version} registered successfully.")
        print(f"Active: {args.activate}")

    finally:
        db.close()


if __name__ == "__main__":
    main()