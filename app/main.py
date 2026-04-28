from fastapi import FastAPI

from app.api.routes_health import router as health_router
from app.api.routes_predict import router as predict_router
from app.api.routes_status import router as status_router
from app.core.config import settings
from app.api.routes_callback_mock import router as callback_mock_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_models import router as models_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, prefix=settings.api_internal_prefix)
    app.include_router(predict_router, prefix=settings.api_internal_prefix)
    app.include_router(status_router, prefix=settings.api_internal_prefix)

    app.include_router(callback_mock_router, prefix=settings.api_internal_prefix)
    app.include_router(models_router, prefix=settings.api_internal_prefix)

    return app


app = create_app()