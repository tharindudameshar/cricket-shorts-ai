import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.short import ExportPlatform, GeneratedShort
from app.schemas.short import ExportRequest, ShortResponse
from app.services.pipeline.metadata import platform_label

router = APIRouter(prefix="/shorts", tags=["shorts"])


@router.get("", response_model=list[ShortResponse])
async def all_shorts(db: AsyncSession = Depends(get_db)) -> list[ShortResponse]:
    result = await db.execute(
        select(GeneratedShort).order_by(GeneratedShort.viral_score.desc()).limit(100)
    )
    out = []
    for s in result.scalars().all():
        item = ShortResponse.model_validate(s)
        item.download_url = f"/api/files/{s.job_id}/{Path(s.file_path).name}"
        if s.thumbnail_path:
            item.thumbnail_url = f"/api/files/{s.job_id}/{Path(s.thumbnail_path).name}"
        out.append(item)
    return out


@router.post("/export")
async def export_shorts(
    body: ExportRequest,
    job_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Re-render shorts for target platform FPS (metadata update)."""
    query = select(GeneratedShort)
    if job_id:
        query = query.where(GeneratedShort.job_id == job_id)
    if body.short_ids:
        query = query.where(GeneratedShort.id.in_(body.short_ids))
    result = await db.execute(query)
    shorts = list(result.scalars().all())
    if not shorts:
        raise HTTPException(404, "No shorts found")

    for s in shorts:
        s.platform = body.platform
        s.fps = body.fps
    await db.commit()

    return {
        "exported": len(shorts),
        "platform": platform_label(body.platform),
        "fps": body.fps,
        "resolution": "1080x1920",
        "format": "MP4",
        "message": "Export presets applied. Download from gallery.",
    }


@router.post("/publish/{platform}")
async def publish_stub(platform: str) -> dict:
    """Placeholder for OAuth publishing integrations."""
    return {
        "status": "not_configured",
        "platform": platform,
        "message": "Connect YouTube/TikTok/Instagram APIs in settings to enable one-click publish.",
    }
