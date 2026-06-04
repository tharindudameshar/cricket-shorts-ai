from app.models.highlight import HighlightType
from app.services.pipeline.types import DetectedMoment

CAPTIONS: dict[HighlightType, list[str]] = {
    HighlightType.SIX: ["WHAT A SIX! 🚀", "MAXIMUM! 🚀", "INTO THE STANDS! 🚀"],
    HighlightType.FOUR: ["FOUR RUNS! ⚡", "BOUNDARY! ⚡"],
    HighlightType.WICKET: ["WICKET! 🔥", "GONE! 🔥", "HOWZAT! 🔥"],
    HighlightType.CATCH: ["UNBELIEVABLE CATCH 😱", "SENSATIONAL CATCH 😱"],
    HighlightType.RUN_OUT: ["RUN OUT! 😤", "DIRECT HIT! 😤"],
    HighlightType.HAT_TRICK: ["HAT-TRICK ALERT 🔥", "THREE IN THREE 🔥"],
    HighlightType.MILESTONE_50: ["FIFTY! 🎯", "HALF CENTURY! 🎯"],
    HighlightType.MILESTONE_100: ["CENTURY! 💯", "HUNDRED! 💯"],
    HighlightType.DRS: ["DRS REVIEW 👀", "THIRD UMPIRE 👀"],
    HighlightType.LAST_OVER: ["LAST BALL THRILLER 🤯", "FINAL OVER DRAMA 🤯"],
    HighlightType.CROWD_REACTION: ["CROWD GOES WILD 📣"],
    HighlightType.CELEBRATION: ["WHAT A CELEBRATION 🎉"],
    HighlightType.HIGH_EXCITEMENT: ["PURE CHAOS 🔥", "INSANE MOMENT 🔥"],
}

TITLES: dict[HighlightType, str] = {
    HighlightType.SIX: "Massive Six",
    HighlightType.FOUR: "Boundary",
    HighlightType.WICKET: "Wicket Fall",
    HighlightType.CATCH: "Stunning Catch",
    HighlightType.RUN_OUT: "Run Out Drama",
    HighlightType.HAT_TRICK: "Hat-Trick",
    HighlightType.MILESTONE_50: "Fifty Milestone",
    HighlightType.MILESTONE_100: "Century",
    HighlightType.DRS: "DRS Review",
    HighlightType.LAST_OVER: "Last Over Thriller",
    HighlightType.CROWD_REACTION: "Crowd Eruption",
    HighlightType.CELEBRATION: "Player Celebration",
    HighlightType.HIGH_EXCITEMENT: "Highlight Moment",
}


def _classify_peak(
    vis_score: float,
    audio_score: float,
    signals,
) -> HighlightType:
    if signals.wicket_graphic > 0.5 or (vis_score > 0.7 and audio_score > 0.6):
        if signals.celebration > 0.5:
            return HighlightType.CATCH
        return HighlightType.WICKET
    if signals.scoreboard_change > 0.55 and audio_score > 0.75:
        return HighlightType.SIX
    if signals.scoreboard_change > 0.4 and audio_score > 0.55:
        return HighlightType.FOUR
    if signals.replay_graphic > 0.25:
        return HighlightType.DRS
    if signals.crowd_motion > 0.6:
        return HighlightType.CROWD_REACTION
    if signals.celebration > 0.45:
        return HighlightType.CELEBRATION
    if audio_score > 0.8:
        return HighlightType.LAST_OVER
    return HighlightType.HIGH_EXCITEMENT


def merge_peaks_to_moments(
    frame_scores: list[tuple[float, float, object]],
    audio_peaks: list[float],
    duration: float,
    min_clip: float = 15.0,
    max_clip: float = 60.0,
) -> list[DetectedMoment]:
    """Cluster high-excitement regions into clip windows."""
    candidates: list[tuple[float, float, HighlightType, float]] = []

    for ts, combined, sig in frame_scores:
        if combined < 0.55:
            continue
        htype = _classify_peak(
            sig.scoreboard_change + sig.wicket_graphic,
            combined,
            sig,
        )
        candidates.append((ts, combined, htype, combined))

    for peak in audio_peaks:
        candidates.append((peak, 0.85, HighlightType.CROWD_REACTION, 0.85))

    if not candidates:
        return []

    candidates.sort(key=lambda x: x[0])
    moments: list[DetectedMoment] = []
    used_ranges: list[tuple[float, float]] = []

    for ts, score, htype, excitement in sorted(
        candidates, key=lambda x: x[1], reverse=True
    ):
        start = max(0, ts - 5)
        end = min(duration, ts + max(min_clip, 12))
        if end - start > max_clip:
            start = end - max_clip
        overlap = any(not (end < u0 or start > u1) for u0, u1 in used_ranges)
        if overlap:
            continue
        used_ranges.append((start, end))
        cap_list = CAPTIONS.get(htype, CAPTIONS[HighlightType.HIGH_EXCITEMENT])
        caption = cap_list[len(moments) % len(cap_list)]
        viral = min(99.0, excitement * 100 + (10 if htype in (HighlightType.SIX, HighlightType.HAT_TRICK) else 0))
        moments.append(
            DetectedMoment(
                highlight_type=htype,
                title=TITLES.get(htype, "Cricket Highlight"),
                caption=caption,
                start_time=start,
                end_time=end,
                excitement_score=round(excitement, 3),
                viral_score=round(viral, 1),
            )
        )
        if len(moments) >= 20:
            break

    moments.sort(key=lambda m: m.excitement_score, reverse=True)
    return moments
