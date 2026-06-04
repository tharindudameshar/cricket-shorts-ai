from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.highlight import HighlightType


class HighlightResponse(BaseModel):
    id: UUID
    job_id: UUID
    highlight_type: HighlightType
    title: str
    caption: str
    start_time: float
    end_time: float
    excitement_score: float
    viral_score: float
    rank: int
    player_name: str | None
    team_name: str | None
    commentary_snippet: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
