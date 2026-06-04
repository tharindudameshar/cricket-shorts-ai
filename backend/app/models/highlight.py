import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HighlightType(str, enum.Enum):
    SIX = "six"
    FOUR = "four"
    WICKET = "wicket"
    RUN_OUT = "run_out"
    CATCH = "catch"
    STUMPING = "stumping"
    HAT_TRICK = "hat_trick"
    MILESTONE_50 = "milestone_50"
    MILESTONE_100 = "milestone_100"
    CLOSE_CALL = "close_call"
    DRS = "drs"
    CROWD_REACTION = "crowd_reaction"
    LAST_OVER = "last_over"
    SUPER_OVER = "super_over"
    FUNNY = "funny"
    CELEBRATION = "celebration"
    HIGH_EXCITEMENT = "high_excitement"


class Highlight(Base):
    __tablename__ = "highlights"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("processing_jobs.id", ondelete="CASCADE")
    )
    highlight_type: Mapped[HighlightType] = mapped_column(Enum(HighlightType))
    title: Mapped[str] = mapped_column(String(256))
    caption: Mapped[str] = mapped_column(String(512), default="")
    start_time: Mapped[float] = mapped_column(Float)
    end_time: Mapped[float] = mapped_column(Float)
    excitement_score: Mapped[float] = mapped_column(Float, default=0.0)
    viral_score: Mapped[float] = mapped_column(Float, default=0.0)
    rank: Mapped[int] = mapped_column(Integer, default=0)
    player_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    team_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    commentary_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    job = relationship("ProcessingJob", back_populates="highlights")
    shorts = relationship("GeneratedShort", back_populates="highlight")
