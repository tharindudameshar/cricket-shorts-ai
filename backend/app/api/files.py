import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.storage import StorageService

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/{job_id}/{filename}")
async def serve_file(job_id: uuid.UUID, filename: str) -> FileResponse:
    storage = StorageService()
    job_dir = storage.job_dir(job_id)
    for sub in ["shorts", "thumbnails", ""]:
        candidate = job_dir / sub / filename if sub else job_dir / filename
        if candidate.exists() and candidate.is_file():
            media = "video/mp4" if filename.endswith(".mp4") else "image/jpeg"
            return FileResponse(candidate, media_type=media, filename=filename)
    raise HTTPException(404, "File not found")
