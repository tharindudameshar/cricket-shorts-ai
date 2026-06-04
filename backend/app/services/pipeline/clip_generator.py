import subprocess
from pathlib import Path

from app.config import get_settings
from app.services.pipeline.types import DetectedMoment


def generate_vertical_short(
    video_path: str,
    moment: DetectedMoment,
    output_path: Path,
    fps: int = 30,
    slow_motion: bool = False,
) -> Path:
    """
    Crop landscape to 9:16 with center-weighted smart crop, optional slow-mo.
    """
    settings = get_settings()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    duration = moment.end_time - moment.start_time
    slow_filter = ""
    if slow_motion and moment.highlight_type.value in (
        "wicket",
        "catch",
        "stumping",
        "run_out",
    ):
        slow_filter = ",setpts=1.4*PTS"

    vf = (
        f"crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
        f"scale=1080:1920:flags=lanczos,"
        f"fps={fps}"
        f"{slow_filter}"
    )

    cmd = [
        settings.ffmpeg_path,
        "-y",
        "-ss",
        str(moment.start_time),
        "-i",
        video_path,
        "-t",
        str(duration),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def generate_thumbnail(video_path: str, timestamp: float, output_path: Path) -> Path:
    settings = get_settings()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        settings.ffmpeg_path,
        "-y",
        "-ss",
        str(timestamp + 1),
        "-i",
        video_path,
        "-vframes",
        "1",
        "-vf",
        "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path
