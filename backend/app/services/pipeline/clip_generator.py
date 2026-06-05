import subprocess
from pathlib import Path

from app.config import get_settings
from app.services.pipeline.types import DetectedMoment
from app.services.pipeline.video_info import get_source_fps, get_video_info


def _target_size() -> tuple[int, int]:
    settings = get_settings()
    mode = settings.short_output_mode.lower()
    if mode == "1080":
        return 1080, 1920
    return settings.short_output_width, settings.short_output_height


def output_dimensions(video_path: str) -> tuple[int, int]:
    settings = get_settings()
    info = get_video_info(video_path)
    mode = settings.short_output_mode.lower()

    if info.is_vertical:
        if mode == "native":
            return info.width, info.height
        return _target_size()

    return _target_size()


def output_fps(video_path: str) -> float:
    return get_source_fps(video_path)


def build_output_filter(
    video_path: str,
    fps: float | None = None,
    slow_filter: str = "",
) -> str | None:
    """
    Portrait: never crop. native = no scale; 4k/1080 = scale to target height.
    Landscape: center-crop to 9:16 then scale.
    When preserve_source_fps: no fps= filter (keeps original frame rate).
    """
    settings = get_settings()
    info = get_video_info(video_path)
    mode = settings.short_output_mode.lower()
    out_w, out_h = _target_size()

    suffix = ""
    if fps is not None and not settings.short_preserve_source_fps:
        suffix = f",fps={fps}{slow_filter}"
    elif slow_filter:
        suffix = slow_filter

    if info.is_vertical:
        if mode == "native":
            return suffix.lstrip(",") if suffix else None
        vf = f"scale={out_w}:{out_h}:flags=lanczos"
        return f"{vf}{suffix}" if suffix else vf

    return (
        f"crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
        f"scale={out_w}:{out_h}:flags=lanczos"
        f"{suffix}"
    )


def _encode_cmd(
    video_path: str,
    start: float,
    duration: float,
    output_path: Path,
    vf: str | None,
) -> list[str]:
    settings = get_settings()
    cmd = [
        settings.ffmpeg_path,
        "-y",
        "-ss",
        str(start),
        "-i",
        video_path,
        "-t",
        str(duration),
    ]
    if vf:
        cmd.extend(["-vf", vf])
    cmd.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            settings.short_preset,
            "-crf",
            str(settings.short_crf),
            "-maxrate",
            settings.short_video_bitrate,
            "-bufsize",
            "40M",
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            "-movflags",
            "+faststart",
            "-threads",
            "0",
            str(output_path),
        ]
    )
    return cmd


def generate_vertical_short(
    video_path: str,
    moment: DetectedMoment,
    output_path: Path,
    slow_motion: bool = False,
) -> Path:
    settings = get_settings()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    duration = moment.end_time - moment.start_time
    source_fps = get_source_fps(video_path)

    slow_filter = ""
    if slow_motion and moment.highlight_type.value in (
        "wicket",
        "catch",
        "stumping",
        "run_out",
    ):
        slow_filter = ",setpts=1.4*PTS"

    force_fps = None if settings.short_preserve_source_fps else source_fps
    vf = build_output_filter(video_path, force_fps, slow_filter)

    cmd = _encode_cmd(video_path, moment.start_time, duration, output_path, vf)
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def generate_thumbnail(video_path: str, timestamp: float, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    vf = build_output_filter(video_path, fps=None)
    cmd = [
        get_settings().ffmpeg_path,
        "-y",
        "-ss",
        str(timestamp + 1),
        "-i",
        video_path,
        "-vframes",
        "1",
    ]
    if vf:
        cmd.extend(["-vf", vf])
    cmd.append(str(output_path))
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path
