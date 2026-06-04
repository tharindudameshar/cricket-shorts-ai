import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.highlight import Highlight
from app.models.job import JobSource, JobStatus, ProcessingJob
from app.models.short import GeneratedShort
from app.schemas.highlight import HighlightResponse
from app.schemas.job import (
    AnalyticsResponse,
    JobCreate,
    JobCreateYouTube,
    JobListItem,
    JobResponse,
)
from app.schemas.short import ShortResponse
from app.services.storage import StorageService
from app.services.youtube import download_youtube

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobListItem])
async def list_jobs(db: AsyncSession = Depends(get_db)) -> list[ProcessingJob]:
    result = await db.execute(
        select(ProcessingJob).order_by(ProcessingJob.created_at.desc()).limit(50)
    )
    return list(result.scalars().all())


@router.get("/analytics", response_model=AnalyticsResponse)
async def analytics(db: AsyncSession = Depends(get_db)) -> AnalyticsResponse:
    jobs_count = await db.scalar(select(func.count()).select_from(ProcessingJob))
    completed = await db.scalar(
        select(func.count())
        .select_from(ProcessingJob)
        .where(ProcessingJob.status == JobStatus.COMPLETED)
    )
    hl_count = await db.scalar(select(func.count()).select_from(Highlight))
    short_count = await db.scalar(select(func.count()).select_from(GeneratedShort))
    avg_viral = await db.scalar(select(func.avg(Highlight.viral_score))) or 0.0

    type_rows = await db.execute(
        select(Highlight.highlight_type, func.count())
        .group_by(Highlight.highlight_type)
        .order_by(func.count().desc())
        .limit(8)
    )
    top_types = [
        {"type": row[0].value, "count": row[1]} for row in type_rows.all()
    ]

    return AnalyticsResponse(
        total_jobs=jobs_count or 0,
        completed_jobs=completed or 0,
        total_highlights=hl_count or 0,
        total_shorts=short_count or 0,
        avg_viral_score=round(float(avg_viral), 1),
        top_highlight_types=top_types,
        processing_hours_saved=round((short_count or 0) * 0.25, 1),
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> ProcessingJob:
    job = await _get_job_or_404(db, job_id)
    return job


@router.get("/{job_id}/highlights", response_model=list[HighlightResponse])
async def job_highlights(
    job_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[Highlight]:
    await _get_job_or_404(db, job_id)
    result = await db.execute(
        select(Highlight)
        .where(Highlight.job_id == job_id)
        .order_by(Highlight.rank)
    )
    return list(result.scalars().all())


@router.get("/{job_id}/shorts", response_model=list[ShortResponse])
async def job_shorts(
    job_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[ShortResponse]:
    await _get_job_or_404(db, job_id)
    storage = StorageService()
    result = await db.execute(
        select(GeneratedShort)
        .where(GeneratedShort.job_id == job_id)
        .order_by(GeneratedShort.viral_score.desc())
    )
    shorts = []
    for s in result.scalars().all():
        item = ShortResponse.model_validate(s)
        item.download_url = f"/api/files/{job_id}/{Path(s.file_path).name}"
        if s.thumbnail_path:
            item.thumbnail_url = f"/api/files/{job_id}/{Path(s.thumbnail_path).name}"
        _ = storage
        shorts.append(item)
    return shorts


@router.post("/upload", response_model=JobResponse)
async def upload_video(
    file: UploadFile = File(...),
    title: str = "Cricket Match",
    league: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> ProcessingJob:
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(400, "File must be a video")

    job = ProcessingJob(
        title=title,
        source=JobSource.UPLOAD,
        league=league,
        status=JobStatus.PENDING,
        status_message="Upload received — queued for processing",
    )
    db.add(job)
    await db.flush()

    storage = StorageService()
    data = await file.read()
    ext = Path(file.filename or "video.mp4").suffix or ".mp4"
    path = storage.save_upload(job.id, f"source{ext}", data)
    job.video_path = path
    await db.commit()
    await db.refresh(job)
    return job


@router.post("/youtube", response_model=JobResponse)
async def youtube_job(
    body: JobCreateYouTube,
    db: AsyncSession = Depends(get_db),
) -> ProcessingJob:
    job = ProcessingJob(
        title=body.title or "YouTube Match",
        source=JobSource.YOUTUBE,
        source_url=body.url,
        league=body.league,
        status=JobStatus.DOWNLOADING,
        status_message="Downloading from YouTube...",
    )
    db.add(job)
    await db.flush()

    storage = StorageService()
    try:
        out_dir = storage.job_dir(job.id)
        filepath, yt_title = download_youtube(body.url, out_dir)
        job.video_path = filepath
        if not body.title:
            job.title = yt_title[:512]
        job.status = JobStatus.PENDING
        job.status_message = "Download complete — queued for AI analysis"
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.status_message = "YouTube download failed"

    await db.commit()
    await db.refresh(job)
    return job


@router.post("/batch", response_model=list[JobResponse])
async def batch_youtube(
    urls: list[str],
    league: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[ProcessingJob]:
    jobs: list[ProcessingJob] = []
    for url in urls[:10]:
        body = JobCreateYouTube(url=url, league=league)
        job = ProcessingJob(
            title=body.title or "YouTube Match",
            source=JobSource.YOUTUBE,
            source_url=body.url,
            league=body.league,
            status=JobStatus.DOWNLOADING,
            status_message="Downloading from YouTube...",
        )
        db.add(job)
        await db.flush()
        storage = StorageService()
        try:
            out_dir = storage.job_dir(job.id)
            filepath, yt_title = download_youtube(body.url, out_dir)
            job.video_path = filepath
            job.title = yt_title[:512]
            job.status = JobStatus.PENDING
            job.status_message = "Download complete — queued"
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
        await db.commit()
        await db.refresh(job)
        jobs.append(job)
    return jobs


async def _get_job_or_404(db: AsyncSession, job_id: uuid.UUID) -> ProcessingJob:
    result = await db.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Job not found")
    return job
