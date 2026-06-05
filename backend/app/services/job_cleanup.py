import shutil
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobStatus, ProcessingJob
from app.services.storage import StorageService


async def delete_job_by_id(session: AsyncSession, job_id: uuid.UUID) -> bool:
    result = await session.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        return False

    storage = StorageService()
    job_dir = storage.job_dir(job_id)
    await session.delete(job)
    await session.commit()

    if job_dir.exists():
        shutil.rmtree(job_dir, ignore_errors=True)
    return True


async def delete_jobs_by_status(
    session: AsyncSession, statuses: list[JobStatus]
) -> int:
    result = await session.execute(
        select(ProcessingJob).where(ProcessingJob.status.in_(statuses))
    )
    jobs = list(result.scalars().all())
    storage = StorageService()

    for job in jobs:
        job_dir = storage.job_dir(job.id)
        await session.delete(job)
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)

    await session.commit()
    return len(jobs)
