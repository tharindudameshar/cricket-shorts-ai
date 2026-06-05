import subprocess
from dataclasses import dataclass
from functools import lru_cache

from app.config import get_settings


def _ffprobe_path() -> str:
    settings = get_settings()
    return settings.ffmpeg_path.replace("ffmpeg", "ffprobe")


@dataclass
class VideoInfo:
    width: int
    height: int
    duration: float
    fps: float = 30.0

    @property
    def is_vertical(self) -> bool:
        """True when source is portrait (e.g. 9:16 phone/DJI vertical)."""
        if self.width <= 0 or self.height <= 0:
            return False
        return self.height > self.width

    @property
    def aspect_ratio(self) -> float:
        if self.height <= 0:
            return 0.0
        return self.width / self.height


def _parse_frame_rate(value: str) -> float:
    value = value.strip()
    if not value or value == "0/0":
        return 0.0
    if "/" in value:
        num, den = value.split("/", 1)
        den_f = float(den)
        return float(num) / den_f if den_f else 0.0
    return float(value)


@lru_cache(maxsize=32)
def get_video_info(video_path: str) -> VideoInfo:
    probe = _ffprobe_path()
    width, height = 0, 0
    fps = 0.0
    try:
        stream = subprocess.run(
            [
                probe,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height,r_frame_rate,avg_frame_rate",
                "-of",
                "csv=p=0",
                video_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        parts = stream.stdout.strip().split(",")
        if len(parts) >= 2:
            width = int(float(parts[0]))
            height = int(float(parts[1]))
        if len(parts) >= 3:
            fps = _parse_frame_rate(parts[2])
        if fps <= 0 and len(parts) >= 4:
            fps = _parse_frame_rate(parts[3])
    except Exception:
        pass

    duration = 0.0
    try:
        dur = subprocess.run(
            [
                probe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        duration = float(dur.stdout.strip())
    except Exception:
        pass

    return VideoInfo(width=width, height=height, duration=duration, fps=fps or 30.0)


def get_source_fps(video_path: str) -> float:
    info = get_video_info(video_path)
    return info.fps if info.fps > 0 else 30.0


def get_video_duration(video_path: str) -> float:
    return get_video_info(video_path).duration
