"""Image compressor batch-start endpoint."""

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.api import API_PREFIX
from app.modules.compression.routes.job_creator import (
    start_compression,
)


def create_images_compress_router() -> APIRouter:
    image_router = APIRouter(
        prefix=f"{API_PREFIX}/images",
        tags=["Image Compression"],
    )

    @image_router.post("/compress")
    async def compress_images(
        background_tasks: BackgroundTasks,
        files: list[UploadFile] = File(...),
        output_format: str = Form("auto"),
        quality: int | None = Form(None),
        compression_preset: str = Form("balanced"),
        max_dimension: int | None = Form(None),
        target_size: int | None = Form(None),
        remove_metadata: bool = Form(True),
    ):
        if quality is not None and (quality < 10 or quality > 100):
            raise HTTPException(
                status_code=400,
                detail="Quality must be between 10 and 100.",
            )

        return await start_compression(
            background_tasks=background_tasks,
            files=files,
            image_output_format=output_format,
            compression_preset=compression_preset,
            max_dimension=max_dimension,
            target_size_kb=target_size,
            strip_metadata=remove_metadata,
            quality=quality,
            tool_id="image_compressor",
        )

    return image_router
