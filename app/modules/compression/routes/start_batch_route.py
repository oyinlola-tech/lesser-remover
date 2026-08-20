"""PDF compressor batch-start endpoint."""

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    UploadFile,
)

from app.api import API_PREFIX
from app.core.capabilities import capability_registry
from app.modules.compression.routes.job_creator import (
    start_compression,
)


def create_batch_start_router() -> APIRouter:
    router = APIRouter(
        prefix=f"{API_PREFIX}/compression",
        tags=["Compression"],
    )

    @router.post("/batch/start")
    async def start_batch_compression(
        background_tasks: BackgroundTasks,
        files: list[UploadFile] = File(...),
        image_output_format: str = "webp",
        compression_preset: str = "balanced",
        max_dimension: int | None = None,
        target_size_kb: int | None = None,
        strip_metadata: bool = True,
        quality: int | None = None,
    ):
        if quality is not None and (quality < 10 or quality > 100):
            raise HTTPException(
                status_code=400,
                detail="Quality must be between 10 and 100.",
            )

        if not capability_registry.is_available("pdf-compressor"):
            raise HTTPException(
                status_code=503,
                detail="PDF compression is unavailable in the current environment.",
            )

        return await start_compression(
            background_tasks=background_tasks,
            files=files,
            image_output_format=image_output_format,
            compression_preset=compression_preset,
            max_dimension=max_dimension,
            target_size_kb=target_size_kb,
            strip_metadata=strip_metadata,
            quality=quality,
            tool_id="pdf_compressor",
        )

    return router
