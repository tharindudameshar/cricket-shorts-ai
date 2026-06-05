from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from app.models.job import JobSource, JobStatus


class JobCreate(BaseModel):
    title: str = "Cricket Match"
    league: str | None = None


class JobCreateYouTube(BaseModel):
    url: str
    title: str | None = None
    league: str | None = Field(None, description="ipl | icc | generic")


class JobListItem(BaseModel):
    id: UUID
    title: str
    status: JobStatus
    progress: float
    highlight_count: int
    short_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class JobResponse(BaseModel):
    id: UUID
    title: str
    source: JobSource
    source_url: str | None
    status: JobStatus
    progress: float
    status_message: str
    duration_seconds: float | None
    league: str | None
    error_message: str | None
    highlight_count: int
    short_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnalyticsResponse(BaseModel):
    total_jobs: int
    completed_jobs: int
    total_highlights: int
    total_shorts: int
    avg_viral_score: float
    top_highlight_types: list[dict[str, int]]
    processing_hours_saved: float


class BatchFolderRequest(BaseModel):
    folder_path: str | None = Field(
        None,
        description="Absolute or storage-relative inbox path. Defaults to BATCH_INBOX_FOLDER.",
    )
    league: str | None = Field(None, description="ipl | icc | generic")
    max_files: int | None = Field(None, ge=1, le=100)


class BatchFolderResponse(BaseModel):
    inbox_path: str
    scanned: int
    queued: int
    skipped: int
    failed: int
    errors: list[str]
    jobs: list[JobResponse]
