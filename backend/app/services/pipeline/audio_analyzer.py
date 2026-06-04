from pathlib import Path
import subprocess
import tempfile

import librosa
import numpy as np

from app.config import get_settings


def extract_audio_wav(video_path: str) -> str:
    settings = get_settings()
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    cmd = [
        settings.ffmpeg_path,
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        tmp.name,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return tmp.name


def analyze_audio_excitement(
    video_path: str,
    hop_length: int = 512,
) -> tuple[np.ndarray, np.ndarray, list[float]]:
    """
    Returns (times, excitement_curve, peak_timestamps).
    Excitement from RMS energy + spectral flux spikes (crowd/commentary).
    """
    wav_path = extract_audio_wav(video_path)
    try:
        y, sr = librosa.load(wav_path, sr=16000, mono=True)
        rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
        flux = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)

        rms_n = (rms - rms.min()) / (rms.max() - rms.min() + 1e-8)
        flux_n = (flux - flux.min()) / (flux.max() - flux.min() + 1e-8)
        min_len = min(len(rms_n), len(flux_n))
        excitement = 0.6 * rms_n[:min_len] + 0.4 * flux_n[:min_len]
        times = times[:min_len]

        threshold = np.percentile(excitement, 92)
        peaks: list[float] = []
        for i in range(1, len(excitement) - 1):
            if excitement[i] > threshold and excitement[i] >= excitement[i - 1] and excitement[i] >= excitement[i + 1]:
                peaks.append(float(times[i]))
        return times, excitement, peaks
    finally:
        Path(wav_path).unlink(missing_ok=True)
