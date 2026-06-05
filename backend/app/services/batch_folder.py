"""Scan an inbox folder and queue each video as a processing job."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.models.job import JobSource, JobStatus, ProcessingJob
from app.services.storage import StorageService

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"}


@dataclass
class BatchFolderResult:
    inbox_path: str
    scanned: int = 0
    queued: int = 0
    skipped: int = 0
    failed: int = 0
    jobs: list[ProcessingJob] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def resolve_inbox(folder: str | Path | None, settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    path = Path(folder) if folder else Path(settings.batch_inbox_folder)
    if not path.is_absolute():
        path = (settings.storage_root / path).resolve()
    return path


def ensure_inbox_dirs(folder: Path) -> tuple[Path, Path, Path]:
    processed = folder / "processed"
    failed = folder / "failed"
    folder.mkdir(parents=True, exist_ok=True)
    processed.mkdir(exist_ok=True)
    failed.mkdir(exist_ok=True)
    return folder, processed, failed


def list_inbox_videos(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    videos: list[Path] = []
    for entry in sorted(folder.iterdir()):
        if not entry.is_file():
            continue
        if entry.name.startswith("."):
            continue
        if entry.suffix.lower() not in VIDEO_EXTENSIONS:
            continue
        videos.append(entry)
    return videos


def inbox_status(folder: Path | None = None) -> dict:
    settings = get_settings()
    inbox = resolve_inbox(folder, settings)
    inbox, processed, failed = ensure_inbox_dirs(inbox)
    pending = list_inbox_videos(inbox)
    done = list(processed.glob("*")) if processed.exists() else []
    errors = list(failed.glob("*")) if failed.exists() else []
    return {
        "inbox_path": str(inbox),
        "pending_count": len(pending),
        "pending_files": [p.name for p in pending],
        "processed_count": len([f for f in done if f.is_file()]),
        "failed_count": len([f for f in errors if f.is_file()]),
        "auto_scan_enabled": settings.batch_auto_scan,
    }


async def ingest_inbox_folder(
    session: AsyncSession,
    folder: str | Path | None = None,
    league: str | None = None,
    max_files: int | None = None,
) -> BatchFolderResult:
    settings = get_settings()
    inbox = resolve_inbox(folder, settings)
    inbox, processed_dir, failed_dir = ensure_inbox_dirs(inbox)
    limit = max_files if max_files is not None else settings.batch_max_files_per_scan
    storage = StorageService()

    result = BatchFolderResult(inbox_path=str(inbox))
    videos = list_inbox_videos(inbox)[:limit]
    result.scanned = len(videos)

    for video_path in videos:
        size_mb = video_path.stat().st_size / (1024 * 1024)
        if settings.batch_max_file_size_mb > 0 and size_mb > settings.batch_max_file_size_mb:
            result.skipped += 1
            result.errors.append(
                f"{video_path.name}: too large ({size_mb:.0f} MB). "
                f"Max {settings.batch_max_file_size_mb} MB — raise BATCH_MAX_FILE_SIZE_MB or set 0."
            )
            continue

        title = video_path.stem.replace("_", " ").replace("-", " ")[:512]
        job = ProcessingJob(
            title=title or video_path.name,
            source=JobSource.BATCH,
            league=league,
            status=JobStatus.PENDING,
            status_message="Queued from batch inbox folder",
        )
        session.add(job)
        await session.flush()

        try:
            dest_dir = storage.job_dir(job.id)
            ext = video_path.suffix.lower() or ".mp4"
            dest = dest_dir / f"source{ext}"
            # Move (not copy) to avoid doubling disk use on large files
            shutil.move(str(video_path), str(dest))
            job.video_path = str(dest)
            result.queued += 1
            result.jobs.append(job)
        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            job.status_message = "Batch ingest failed"
            result.failed += 1
            result.errors.append(f"{video_path.name}: {exc}")
            try:
                dest_failed = failed_dir / video_path.name
                if video_path.exists():
                    if dest_failed.exists():
                        dest_failed = failed_dir / f"{video_path.stem}_{job.id.hex[:8]}{video_path.suffix}"
                    shutil.move(str(video_path), str(dest_failed))
            except Exception:
                pass

    await session.commit()
    for job in result.jobs:
        await session.refresh(job)
    return result
