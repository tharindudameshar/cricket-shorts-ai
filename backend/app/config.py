from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = (
        "postgresql+asyncpg://cricket:cricket@localhost:5432/cricket_shorts"
    )
    storage_local_path: str = "./storage"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket: str = "cricket-shorts-uploads"
    ai_demo_mode: bool = True
    yolo_model_path: str = ""
    whisper_model: str = "base"
    ffmpeg_path: str = "ffmpeg"
    openai_api_key: str = ""
    worker_poll_interval: int = 2

    @property
    def use_s3(self) -> bool:
        return bool(self.aws_access_key_id and self.aws_secret_access_key)

    @property
    def storage_root(self) -> Path:
        return Path(self.storage_local_path).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
