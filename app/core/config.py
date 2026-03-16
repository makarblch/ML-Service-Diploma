from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "python-ml-service"
    app_version: str = "1.0.0"
    api_internal_prefix: str = "/api/internal/v1"
    default_model_version: str = "latest"
    log_level: str = "INFO"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "ml_service"
    postgres_user: str = "ml_user"
    postgres_password: str = "ml_password"

    artifacts_root: str = "artifacts"
    models_dir: str = "artifacts/models"
    preprocessors_dir: str = "artifacts/preprocessors"
    schemas_dir: str = "artifacts/schemas"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()