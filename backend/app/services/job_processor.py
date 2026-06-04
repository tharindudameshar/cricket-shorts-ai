import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.highlight import Highlight
from app.models.job import JobStatus, ProcessingJob
from app.models.short import ExportPlatform, GeneratedShort
from app.services.pipeline.clip_generator import generate_thumbnail, generate_vertical_short
from app.services.pipeline.metadata import build_description, build_hashtags
from app.services.pipeline.orchestrator import run_analysis_pipeline
from app.services.storage import StorageService


async def process_job(session: AsyncSession, job_id: uuid.UUID) -> None:
    storage = StorageService()
    result = await session.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job or not job.video_path:
        return

    def update(progress: float, msg: str, status: JobStatus | None = None) -> None:
        job.progress = progress
        job.status_message = msg
        if status:
            job.status = status

    try:
        update(0, "Starting analysis...", JobStatus.ANALYZING)
        await session.commit()

        def on_progress(p: float, msg: str) -> None:
            job.progress = min(70, p * 0.7)
            job.status_message = msg

        pipeline = run_analysis_pipeline(
            job.video_path,
            league=job.league,
            on_progress=on_progress,
        )
        job.duration_seconds = pipeline.duration_seconds

        for rank, moment in enumerate(pipeline.moments, start=1):
            hl = Highlight(
                job_id=job.id,
                highlight_type=moment.highlight_type,
                title=moment.title,
                caption=moment.caption,
                start_time=moment.start_time,
                end_time=moment.end_time,
                excitement_score=moment.excitement_score,
                viral_score=moment.viral_score,
                rank=rank,
                player_name=moment.player_name,
                team_name=moment.team_name,
                commentary_snippet=moment.commentary_snippet,
            )
            session.add(hl)

        job.highlight_count = len(pipeline.moments)
        job.progress = 75
        job.status = JobStatus.GENERATING
        job.status_message = "Generating vertical shorts..."
        await session.commit()

        out_dir = storage.job_dir(job.id) / "shorts"
        thumb_dir = storage.job_dir(job.id) / "thumbnails"
        video = job.video_path

        for rank, moment in enumerate(pipeline.moments, start=1):
            short_id = uuid.uuid4()
            out_file = out_dir / f"{short_id}.mp4"
            thumb_file = thumb_dir / f"{short_id}.jpg"
            slow = moment.highlight_type.value in ("wicket", "catch", "stumping")
            try:
                generate_vertical_short(video, moment, out_file, fps=30, slow_motion=slow)
                generate_thumbnail(video, moment.start_time, thumb_file)
            except Exception:
                out_file.write_bytes(b"")
                thumb_file = None

            hl_result = await session.execute(
                select(Highlight)
                .where(Highlight.job_id == job.id, Highlight.rank == rank)
                .limit(1)
            )
            hl = hl_result.scalar_one_or_none()

            short = GeneratedShort(
                job_id=job.id,
                highlight_id=hl.id if hl else None,
                title=moment.caption,
                description=build_description(moment, job.league),
                hashtags=build_hashtags(moment, job.league),
                file_path=str(out_file),
                thumbnail_path=str(thumb_file) if thumb_file and thumb_file.exists() else None,
                duration_seconds=moment.end_time - moment.start_time,
                platform=ExportPlatform.YOUTUBE_SHORTS,
                viral_score=moment.viral_score,
                views_predicted=int(moment.viral_score * 1200),
            )
            session.add(short)
            job.short_count += 1
            job.progress = 75 + (20 * rank / max(len(pipeline.moments), 1))
            await session.commit()

        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.status_message = f"Created {job.short_count} shorts ready to export"
        await session.commit()
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.status_message = "Processing failed"
        await session.commit()
