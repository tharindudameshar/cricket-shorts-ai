import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class JobSource(str, enum.Enum):
    UPLOAD = "upload"
    YOUTUBE = "youtube"
    BATCH = "batch"


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(512), default="Untitled Match")
    source: Mapped[JobSource] = mapped_column(Enum(JobSource), default=JobSource.UPLOAD)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), default=JobStatus.PENDING, index=True
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    status_message: Mapped[str] = mapped_column(String(512), default="Queued")
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    league: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    highlight_count: Mapped[int] = mapped_column(Integer, default=0)
    short_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    highlights = relationship(
        "Highlight", back_populates="job", cascade="all, delete-orphan"
    )
    shorts = relationship(
        "GeneratedShort", back_populates="job", cascade="all, delete-orphan"
    )
