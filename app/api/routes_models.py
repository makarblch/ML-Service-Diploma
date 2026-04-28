from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.model_registry_repository import ModelRegistryRepository
from app.schemas.model_response import ModelInfoResponse, ModelListResponse

router = APIRouter(tags=["models"])


@router.get(
    "/models",
    response_model=ModelListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_models(
    db: Session = Depends(get_db),
) -> ModelListResponse:
    model_repo = ModelRegistryRepository(db)
    model_records = model_repo.list_models()

    models = [
        ModelInfoResponse(
            model_version=model.model_version,
            model_name=model.model_name,
            is_active=model.is_active,
            description=model.description,
            created_at=model.created_at,
        )
        for model in model_records
    ]

    return ModelListResponse(models=models)