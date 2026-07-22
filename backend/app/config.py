from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./researchiq.db"

    frontend_origin: str = "http://localhost:5173"

    upload_dir: str = "uploads"

    llm_api_key: str | None = None
    llm_base_url: str | None = None
    llm_model: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)