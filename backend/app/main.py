from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import files, jobs, shorts
from app.config import get_settings
from app.database import init_db
from app.services.batch_folder import ensure_inbox_dirs, resolve_inbox


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    settings = get_settings()
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    ensure_inbox_dirs(resolve_inbox(None, settings))
    yield


app = FastAPI(
    title="Cricket Shorts AI",
    description="AI-powered cricket highlight detection and vertical short generation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api")
app.include_router(shorts.router, prefix="/api")
app.include_router(files.router, prefix="/api")

settings = get_settings()
if settings.storage_root.exists():
    app.mount(
        "/storage",
        StaticFiles(directory=str(settings.storage_root)),
        name="storage",
    )


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "demo_mode": settings.ai_demo_mode,
        "short_output_mode": settings.short_output_mode,
        "short_resolution": f"{settings.short_output_width}x{settings.short_output_height}",
    }
