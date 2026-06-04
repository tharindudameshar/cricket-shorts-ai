from dataclasses import dataclass, field

from app.models.highlight import HighlightType


@dataclass
class DetectedMoment:
    highlight_type: HighlightType
    title: str
    caption: str
    start_time: float
    end_time: float
    excitement_score: float
    viral_score: float
    player_name: str | None = None
    team_name: str | None = None
    commentary_snippet: str | None = None


@dataclass
class PipelineResult:
    duration_seconds: float
    moments: list[DetectedMoment] = field(default_factory=list)
    audio_peaks: list[float] = field(default_factory=list)
