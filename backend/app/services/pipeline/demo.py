"""Simulated highlights when AI_DEMO_MODE=true."""

import random

from app.models.highlight import HighlightType
from app.services.pipeline.types import DetectedMoment

DEMO_SEQUENCE: list[tuple[HighlightType, str, str]] = [
    (HighlightType.FOUR, "Powerful Boundary", "FOUR RUNS! ⚡"),
    (HighlightType.SIX, "Massive Six", "WHAT A SIX! 🚀"),
    (HighlightType.WICKET, "Wicket Fall", "WICKET! 🔥"),
    (HighlightType.CATCH, "Stunning Catch", "UNBELIEVABLE CATCH 😱"),
    (HighlightType.DRS, "DRS Review", "DRS REVIEW 👀"),
    (HighlightType.MILESTONE_50, "Fifty Milestone", "FIFTY! 🎯"),
    (HighlightType.SIX, "Another Six", "MAXIMUM! 🚀"),
    (HighlightType.RUN_OUT, "Run Out Drama", "RUN OUT! 😤"),
    (HighlightType.CELEBRATION, "Player Celebration", "WHAT A CELEBRATION 🎉"),
    (HighlightType.LAST_OVER, "Last Over Thriller", "LAST BALL THRILLER 🤯"),
    (HighlightType.CROWD_REACTION, "Crowd Eruption", "CROWD GOES WILD 📣"),
    (HighlightType.HAT_TRICK, "Hat-Trick", "HAT-TRICK ALERT 🔥"),
    (HighlightType.MILESTONE_100, "Century", "CENTURY! 💯"),
    (HighlightType.FUNNY, "Funny Moment", "WAIT WHAT 😂"),
    (HighlightType.SUPER_OVER, "Super Over", "SUPER OVER DRAMA ⚡"),
]


def generate_demo_moments(duration: float, count: int = 15) -> list[DetectedMoment]:
    random.seed(int(duration) % 10000)
    moments: list[DetectedMoment] = []
    spacing = duration / (count + 1)
    for i, (htype, title, caption) in enumerate(DEMO_SEQUENCE[:count]):
        center = spacing * (i + 1)
        clip_len = random.uniform(18, 45)
        start = max(0, center - clip_len / 2)
        end = min(duration, start + clip_len)
        excitement = random.uniform(0.72, 0.98)
        viral = min(99, excitement * 100 + random.uniform(0, 8))
        moments.append(
            DetectedMoment(
                highlight_type=htype,
                title=title,
                caption=caption,
                start_time=round(start, 2),
                end_time=round(end, 2),
                excitement_score=round(excitement, 3),
                viral_score=round(viral, 1),
                player_name=random.choice(["Kohli", "Rohit", "Bumrah", "SKY", "Gill", None]),
                team_name=random.choice(["India", "Mumbai Indians", "RCB", None]),
                commentary_snippet=random.choice(
                    [
                        "What a shot!",
                        "He's gone! Caught behind!",
                        "Into the crowd!",
                        None,
                    ]
                ),
            )
        )
    moments.sort(key=lambda m: m.viral_score, reverse=True)
    return moments
