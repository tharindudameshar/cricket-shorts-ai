from pathlib import Path

import yt_dlp

from app.config import get_settings


def download_youtube(url: str, output_dir: Path) -> tuple[str, str]:
    """Download video; returns (file_path, title)."""
    settings = get_settings()
    output_dir.mkdir(parents=True, exist_ok=True)
    out_template = str(output_dir / "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "outtmpl": out_template,
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "YouTube Match")
        filepath = ydl.prepare_filename(info)
        if not filepath.endswith(".mp4"):
            mp4 = Path(filepath).with_suffix(".mp4")
            if mp4.exists():
                filepath = str(mp4)
        return filepath, title
