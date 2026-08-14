import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    UploadFile,
)
from pathlib import Path
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)
from app.modules.compression.batch_compression_service import (
    batch_compression_service,
)
from app.modules.compression.compression_controller import (
    compression_controller,
)
from app.modules.compression.compression_repository import (
    compression_repository,
)
from app.modules.jobs.job_service import (
    job_service,
)
from app.infrastructure.jobs import local_job_storage
from app.shared.utils.file_util import is_safe_filename
from app.shared.utils.file_util import (
    generate_filename,
)
from app.shared.enums.compression_enum import CompressionLevel

router = APIRouter(
    prefix="/api/compression",
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
):
    if not files:
        logger.warning("Compression request rejected: no files uploaded")
        raise HTTPException(
            status_code=400,
            detail="No files were uploaded.",
        )

    if len(files) > 20:
        logger.warning(
            "Compression request rejected: %s files exceed limit of 20",
            len(files),
        )
        raise HTTPException(
            status_code=400,
            detail="Maximum of 20 files.",
        )

    filenames = [
        file.filename or "file"
        for file in files
    ]

    logger.info(
        "Starting batch compression job for %s files: %s",
        len(filenames),
        filenames,
    )

    job_id = job_service.create(
        filenames
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
        )

        logger.info(
            "Batch compression job created: job_id=%s, files=%s, format=%s, preset=%s",
            job_id,
            len(stored_files),
            image_output_format,
            compression_preset,
        )

    except Exception:
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
