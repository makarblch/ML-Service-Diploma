from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ModelRegistry


class ModelRegistryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_model(self) -> ModelRegistry | None:
        stmt = select(ModelRegistry).where(ModelRegistry.is_active.is_(True))
        return self.db.scalar(stmt)

    def get_model_by_version(self, model_version: str) -> ModelRegistry | None:
        stmt = select(ModelRegistry).where(ModelRegistry.model_version == model_version)
        return self.db.scalar(stmt)