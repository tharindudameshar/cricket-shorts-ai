from pathlib import Path

import cv2
import numpy as np


def extract_frames(
    video_path: str,
    sample_fps: float = 2.0,
    max_frames: int = 5000,
) -> tuple[list[np.ndarray], list[float], float]:
    """Sample frames at sample_fps; returns frames, timestamps, duration."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / native_fps if frame_count else 0.0
    step = max(1, int(native_fps / sample_fps))

    frames: list[np.ndarray] = []
    timestamps: list[float] = []
    idx = 0

    while cap.isOpened() and len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % step == 0:
            frames.append(frame)
            timestamps.append(idx / native_fps)
        idx += 1

    cap.release()
    if duration == 0 and timestamps:
        duration = timestamps[-1]
    return frames, timestamps, duration
