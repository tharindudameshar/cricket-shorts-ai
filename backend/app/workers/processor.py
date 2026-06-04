"""Background worker polling for pending jobs."""

import asyncio
import sys

from sqlalchemy import select

from app.config import get_settings
from app.database import async_session, init_db
from app.models.job import JobStatus, ProcessingJob
from app.services.job_processor import process_job


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


async def main() -> None:
    settings = get_settings()
    await init_db()
    print("Cricket Shorts AI worker started", flush=True)
    while True:
        try:
            worked = await poll_once()
            if not worked:
                await asyncio.sleep(settings.worker_poll_interval)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Worker error: {e}", flush=True)
            await asyncio.sleep(settings.worker_poll_interval)


if __name__ == "__main__":
    asyncio.run(main())
