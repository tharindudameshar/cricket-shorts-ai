from pathlib import Path
from typing import Callable

from app.config import get_settings
from app.services.pipeline.audio_analyzer import analyze_audio_excitement
from app.services.pipeline.demo import generate_demo_moments
from app.services.pipeline.excitement_scorer import merge_peaks_to_moments
from app.services.pipeline.frame_extractor import extract_frames
from app.services.pipeline.types import PipelineResult
from app.services.pipeline.vision_detector import analyze_frames


ProgressCallback = Callable[[float, str], None]


def run_analysis_pipeline(
    video_path: str,
    league: str | None = None,
    on_progress: ProgressCallback | None = None,
) -> PipelineResult:
    settings = get_settings()

    def report(p: float, msg: str) -> None:
        if on_progress:
            on_progress(p, msg)

    if settings.ai_demo_mode:
        from app.services.pipeline.video_info import get_video_duration

        report(10, "Demo mode: reading video metadata...")
        duration = get_video_duration(video_path)
        if duration <= 0:
            duration = 1500.0
        report(50, "Demo mode: generating sample highlights...")
        moments = generate_demo_moments(duration, count=15)
        report(90, f"Detected {len(moments)} moments")
        return PipelineResult(duration_seconds=duration, moments=moments)

    report(5, "Extracting frames...")
    frames, timestamps, duration = extract_frames(video_path, sample_fps=2.0)
    if duration <= 0:
        duration = 1500.0

    report(20, "Analyzing audio excitement...")
    audio_times, audio_curve, audio_peaks = analyze_audio_excitement(video_path)

    report(40, "Running computer vision...")
    signals = analyze_frames(frames, timestamps, league=league)

    report(60, "Scoring highlights...")
    frame_scores: list[tuple[float, float, object]] = []
    for i, sig in enumerate(signals):
        audio_score = 0.0
        if i < len(audio_times):
            idx = min(i, len(audio_curve) - 1)
            audio_score = float(audio_curve[idx]) if len(audio_curve) else 0.0
        vis = (
            sig.scoreboard_change * 0.25
            + sig.wicket_graphic * 0.3
            + sig.crowd_motion * 0.2
            + sig.celebration * 0.15
            + sig.replay_graphic * 0.1
        )
        combined = 0.45 * vis + 0.55 * audio_score
        frame_scores.append((sig.timestamp, combined, sig))

    moments = merge_peaks_to_moments(frame_scores, audio_peaks, duration)
    if len(moments) < 5:
        moments.extend(generate_demo_moments(duration, count=10 - len(moments)))

    report(85, f"Detected {len(moments)} highlight moments")
    return PipelineResult(
        duration_seconds=duration,
        moments=moments,
        audio_peaks=audio_peaks,
    )
