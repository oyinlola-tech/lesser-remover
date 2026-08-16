import logging
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)
from app.api import API_PREFIX
from app.core.capabilities import capability_registry
from app.infrastructure.jobs import local_job_storage
from app.modules.compression.batch_compression_service import (
    batch_compression_service,
)
from app.modules.compression.compression_repository import (
    compression_repository,
)
from app.modules.jobs.job_service import (
    job_service,
)
from app.shared.constants.file_constants import MAX_FILES_PER_BATCH
from app.shared.utils.file_util import (
    generate_filename,
    is_safe_filename,
)

router = APIRouter(
    prefix=f"{API_PREFIX}/compression",
    tags=["Compression"],
)

image_router = APIRouter(
    prefix=f"{API_PREFIX}/images",
    tags=["Image Compression"],
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

    return await _start_compression(
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

    target_size_kb = target_size

    return await _start_compression(
        background_tasks=background_tasks,
        files=files,
        image_output_format=output_format,
        compression_preset=compression_preset,
        max_dimension=max_dimension,
        target_size_kb=target_size_kb,
        strip_metadata=remove_metadata,
        quality=quality,
        tool_id="image_compressor",
    )


async def _start_compression(
    background_tasks: BackgroundTasks,
    files: list[UploadFile],
    image_output_format: str,
    compression_preset: str,
    max_dimension: int | None = None,
    target_size_kb: int | None = None,
    strip_metadata: bool = True,
    quality: int | None = None,
    tool_id: str = "unknown",
) -> dict:
    if not files:
        logger.warning("Compression request rejected: no files uploaded")
        raise HTTPException(
            status_code=400,
            detail="No files were uploaded.",
        )

    if len(files) > MAX_FILES_PER_BATCH:
        logger.warning(
            "Compression request rejected: %s files exceed limit of %s",
            len(files),
            MAX_FILES_PER_BATCH,
        )
        raise HTTPException(
            status_code=400,
            detail=f"Maximum of {MAX_FILES_PER_BATCH} files.",
        )

    if tool_id == "pdf_compressor" and not capability_registry.is_available("pdf-compressor"):
        raise HTTPException(
            status_code=503,
            detail="PDF compression is unavailable in the current environment.",
        )

    filenames = [
        file.filename or "file"
        for file in files
    ]

    logger.info(
        "Starting image compression job for %s files: %s",
        len(filenames),
        filenames,
    )

    job_id = job_service.create(
        filenames,
        tool_id=tool_id,
    )

    stored_files = []

    try:
        for index, file in enumerate(files):

            original_filename = (
                file.filename
                or "file"
            )

            extension = (
                Path(
                    original_filename
                )
                .suffix
                .lower()
                .lstrip(".")
            )

            stored_filename = (
                generate_filename(
                    original_filename,
                    extension=extension,
                )
            )

            total_size = 0

            buffer = bytearray()

            while True:
                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                buffer.extend(chunk)

                total_size += len(chunk)

                if total_size > (
                    50 * 1024 * 1024
                ):
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"{original_filename} "
                            "is larger than the "
                            "50 MB upload limit."
                        ),
                    )

            local_job_storage.save_input(
                job_id,
                stored_filename,
                bytes(buffer),
            )

            file_id = str(index)

            job_service.set_input_filename(
                job_id,
                file_id,
                stored_filename,
            )

            stored_files.append(
                {
                    "id": file_id,
                    "filename": original_filename,
                    "input_filename": stored_filename,
                }
            )

        background_tasks.add_task(
            batch_compression_service.process,
            job_id,
            stored_files,
            image_output_format,
            compression_preset,
            max_dimension,
            target_size_kb,
            strip_metadata,
            quality,
        )

        logger.info(
            "Image compression job created: job_id=%s, files=%s, format=%s, preset=%s, quality=%s",
            job_id,
            len(stored_files),
            image_output_format,
            compression_preset,
            quality,
        )

    except Exception as error:
        logger.exception(
            "Failed to create compression job %s: %s",
            job_id,
            error,
        )
        job_service.cancel(
            job_id
        )

        raise

    return {
        "success": True,
        "job_id": job_id,
        "status": "created",
    }


@router.get("/download/{filename}")
async def download_compressed_file(
    filename: str,
):
    if not is_safe_filename(filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )
    file_path = compression_repository.get(
        filename
    )
    if not file_path.is_file():
        file_path = (
            local_job_storage
            .materialize_download(filename)
        )
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Compressed file not found",
        )
    extension = file_path.suffix.lower()
    content_type_map = {
        ".webp": "image/webp",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
        ".pdf": "application/pdf",
        ".zip": "application/zip",
    }
    content_type = content_type_map.get(
        extension,
        "application/octet-stream",
    )
    try:
        return FileResponse(
            path=file_path,
            media_type=content_type,
            filename=file_path.name,
        )
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Compressed file not found",
        ) from error
