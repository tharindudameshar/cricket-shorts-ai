"""Computer vision: scoreboard, graphics, crowd motion, YOLO players."""

from dataclasses import dataclass

import cv2
import numpy as np

from app.config import get_settings


@dataclass
class FrameSignals:
    timestamp: float
    scoreboard_change: float
    wicket_graphic: float
    replay_graphic: float
    crowd_motion: float
    celebration: float


def _region_motion(prev: np.ndarray, curr: np.ndarray, roi: tuple) -> float:
    x, y, w, h = roi
    p = cv2.cvtColor(prev[y : y + h, x : x + w], cv2.COLOR_BGR2GRAY)
    c = cv2.cvtColor(curr[y : y + h, x : x + w], cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(p, c)
    return float(np.mean(diff)) / 255.0


def _detect_red_overlay(frame: np.ndarray) -> float:
    """Wicket/out graphics often use strong red overlays."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 100, 100])
    upper = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    return float(np.sum(mask > 0)) / (frame.shape[0] * frame.shape[1])


def _scoreboard_region(league: str | None) -> tuple[int, int, int, int]:
    if league == "ipl":
        return (0, 0, int(0.35 * 1920), int(0.12 * 1080))  # scaled at runtime
    return (0, 0, 400, 120)


def analyze_frames(
    frames: list[np.ndarray],
    timestamps: list[float],
    league: str | None = None,
) -> list[FrameSignals]:
    settings = get_settings()
    yolo = None
    if not settings.ai_demo_mode and settings.yolo_model_path:
        try:
            from ultralytics import YOLO

            yolo = YOLO(settings.yolo_model_path)
        except Exception:
            yolo = None

    signals: list[FrameSignals] = []
    prev = frames[0] if frames else None
    h, w = frames[0].shape[:2] if frames else (1080, 1920)
    sb = _scoreboard_region(league)
    sb = (sb[0], sb[1], min(sb[2], w - 1), min(sb[3], h - 1))
    crowd_roi = (int(w * 0.1), int(h * 0.55), int(w * 0.8), int(h * 0.35))

    for i, frame in enumerate(frames):
        ts = timestamps[i]
        sb_change = 0.0
        crowd = 0.0
        if prev is not None:
            sb_change = _region_motion(prev, frame, sb)
            crowd = _region_motion(prev, frame, crowd_roi)
        red = _detect_red_overlay(frame)
        replay = 0.0
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        if np.mean(edges) < 25:
            replay = 0.3
        celebration = crowd * 1.2 if crowd > 0.08 else 0.0
        if yolo:
            _ = yolo(frame, verbose=False)
        signals.append(
            FrameSignals(
                timestamp=ts,
                scoreboard_change=min(sb_change * 3, 1.0),
                wicket_graphic=min(red * 4, 1.0),
                replay_graphic=replay,
                crowd_motion=min(crowd * 2.5, 1.0),
                celebration=min(celebration, 1.0),
            )
        )
        prev = frame
    return signals
