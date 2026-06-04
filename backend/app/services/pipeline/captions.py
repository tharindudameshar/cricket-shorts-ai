from app.config import get_settings


def transcribe_clip(video_path: str, start: float, end: float) -> str:
    """Extract commentary snippet via Whisper (optional)."""
    settings = get_settings()
    if settings.ai_demo_mode:
        return ""
    try:
        import subprocess
        import tempfile
        from pathlib import Path

        import whisper

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        subprocess.run(
            [
                settings.ffmpeg_path,
                "-y",
                "-ss",
                str(start),
                "-to",
                str(end),
                "-i",
                video_path,
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "16000",
                tmp.name,
            ],
            check=True,
            capture_output=True,
        )
        model = whisper.load_model(settings.whisper_model)
        result = model.transcribe(tmp.name)
        Path(tmp.name).unlink(missing_ok=True)
        return (result.get("text") or "").strip()
    except Exception:
        return ""
