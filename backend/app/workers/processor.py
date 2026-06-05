"""Background worker polling for pending jobs and batch inbox folder."""

import asyncio
import sys

from sqlalchemy import select

from app.config import get_settings
from app.database import async_session, init_db
from app.models.job import JobStatus, ProcessingJob
from app.services.batch_folder import ensure_inbox_dirs, ingest_inbox_folder, resolve_inbox
from app.services.job_processor import process_job


async def scan_inbox_if_enabled() -> int:
    settings = get_settings()
    if not settings.batch_auto_scan:
        return 0
    inbox = resolve_inbox(None, settings)
    ensure_inbox_dirs(inbox)
    async with async_session() as session:
        result = await ingest_inbox_folder(session)
    if result.queued:
        print(
            f"Batch inbox: queued {result.queued} video(s) from {result.inbox_path}",
            flush=True,
        )
    return result.queued


async def poll_once() -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(ProcessingJob)
            .where(ProcessingJob.status == JobStatus.PENDING)
            .order_by(ProcessingJob.created_at)
            .limit(1)
        )
        job = result.scalar_one_or_none()
        if not job:
            return False
        job.status = JobStatus.ANALYZING
        job.status_message = "Worker picked up job"
        await session.commit()
        job_id = job.id

    async with async_session() as session:
        await process_job(session, job_id)
    return True


async def recover_stale_jobs(session) -> int:
    """Reset jobs stuck in analyzing/generating (e.g. after worker was killed)."""
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import select

    from app.models.job import JobStatus, ProcessingJob

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=2)
    result = await session.execute(
        select(ProcessingJob).where(
            ProcessingJob.status.in_([JobStatus.ANALYZING, JobStatus.GENERATING]),
            ProcessingJob.updated_at < cutoff,
        )
    )
    jobs = list(result.scalars().all())
    for job in jobs:
        job.status = JobStatus.PENDING
        job.progress = 0
        job.status_message = "Re-queued after worker restart"
    if jobs:
        await session.commit()
    return len(jobs)


async def main() -> None:
    settings = get_settings()
    await init_db()
    inbox = resolve_inbox(None, settings)
    ensure_inbox_dirs(inbox)
    async with async_session() as session:
        recovered = await recover_stale_jobs(session)
    print("Cricket Shorts AI worker started", flush=True)
    if recovered:
        print(f"Recovered {recovered} stuck job(s)", flush=True)
    print(f"Batch inbox folder: {inbox}", flush=True)
    print("Drop videos into the inbox folder to auto-queue jobs.", flush=True)
    scan_counter = 0
    while True:
        try:
            worked = await poll_once()
            if worked:
                scan_counter = 0
                continue
            scan_counter += 1
            if settings.batch_auto_scan and scan_counter >= max(
                1, settings.batch_scan_interval // settings.worker_poll_interval
            ):
                await scan_inbox_if_enabled()
                scan_counter = 0
            await asyncio.sleep(settings.worker_poll_interval)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Worker error: {e}", flush=True)
            await asyncio.sleep(settings.worker_poll_interval)


if __name__ == "__main__":
    asyncio.run(main())
