from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.short import ExportPlatform


class ShortResponse(BaseModel):
    id: UUID
    job_id: UUID
    highlight_id: UUID | None
    title: str
    description: str
    hashtags: str
    file_path: str
    download_url: str | None = None
    thumbnail_url: str | None = None
    duration_seconds: float
    width: int
    height: int
    fps: int
    platform: ExportPlatform
    viral_score: float
    views_predicted: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ExportRequest(BaseModel):
    platform: ExportPlatform = ExportPlatform.YOUTUBE_SHORTS
    fps: int = Field(30, ge=30, le=60)
    short_ids: list[UUID] | None = None
