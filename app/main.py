import asyncio
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import setup_logging
from app.modules.background.background_route import (
    router as background_router,
)
from app.modules.compression.compression_route import (
    router as compression_router,
)
from app.modules.jobs.job_cleanup_service import (
    job_cleanup_service,
)
from app.modules.jobs.job_route import router as job_router

setup_logging()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
app = FastAPI(
    title=settings.app_name,
    description=(
        "Local image background removal and "
        "file compression application"
    ),
    version=settings.app_version,
)
from app.core.exceptions import register_exception_handlers
register_exception_handlers(app)
app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)
app.include_router(background_router)
app.include_router(compression_router)
app.include_router(job_router)

@app.on_event("startup")
async def startup_cleanup():
    await asyncio.to_thread(job_cleanup_service.cleanup_all)
@app.get("/")
async def home():
    return FileResponse(
        FRONTEND_DIR / "index.html",
    )
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "application": settings.app_name,
        "environment": settings.app_env,
    }
