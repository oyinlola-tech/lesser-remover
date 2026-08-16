import logging
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.modules.archive.archive_service import archive_service
from app.modules.compression.compression_repository import (
    compression_repository,
)
from app.modules.compression.compression_schema import (
    BatchCompressionResult,
    CompressionResult,
)
from app.modules.compression.compression_service import (
    compression_service,
)
from app.modules.jobs.job_service import job_service
from app.shared.file_inspection.file_validation import (
    inspect_and_validate,
)
from app.shared.utils.file_util import generate_filename

logger = logging.getLogger(__name__)


class CompressionController:
    async def compress_file(
        self,
        file: UploadFile,
        output_format: str = "webp",
        compression_preset: str = "balanced",
        target_size_kb: int | None = None,
        max_dimension: int | None = None,
    ) -> CompressionResult:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        file_data = await file.read()
        if not file_data:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        inspection = inspect_and_validate(file_data)
        if inspection.category.value == "image":
            if output_format not in {"webp", "jpeg", "png"}:
                raise HTTPException(status_code=400, detail="Unsupported output format")
        elif inspection.category.value == "pdf":
            output_format = "pdf"
        else:
            raise HTTPException(status_code=415, detail="Unsupported file type")

        original_size = len(file_data)
        target_size_bytes = None
        if target_size_kb is not None:
            if target_size_kb < 10:
                raise HTTPException(status_code=400, detail="Target size must be at least 10 KB")
            target_size_bytes = target_size_kb * 1024

        try:
            if inspection.category.value == "image":
                (
                    compressed_data,
                    content_type,
                    _quality,
                    _width,
                    _height,
                ) = compression_service.compress_image(
                    file_data=file_data,
                    preset=compression_preset,
                    output_format=output_format,
                    target_size_bytes=target_size_bytes,
                    max_dimension=max_dimension,
                )
            elif inspection.category.value == "pdf":
                compressed_data, content_type, _pdf_quality = compression_service.compress_pdf(
                    file_data=file_data,
                    preset=compression_preset,
                )
            else:
                raise HTTPException(status_code=415, detail="Unsupported file type")

            if len(compressed_data) >= original_size:
                compressed_data = file_data
                content_type = file.content_type or inspection.mime_type
                extension = Path(file.filename).suffix.lower().lstrip(".")
            else:
                extension = {
                    "webp": "webp",
                    "jpeg": "jpg",
                    "png": "png",
                    "pdf": "pdf",
                }.get(output_format, inspection.extension.lstrip("."))
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except Exception as error:
            raise HTTPException(status_code=400, detail=f"Unable to compress file: {error}") from error

        output_filename = generate_filename(file.filename, extension=extension)
        output_path = compression_repository.save(compressed_data, output_filename)
        compressed_size = len(compressed_data)
        compression_ratio = compressed_size / original_size if original_size else 0
        savings_percent = (1 - compression_ratio) * 100

        return CompressionResult(
            success=True,
            original_filename=file.filename,
            output_filename=output_path.name,
            original_size_bytes=original_size,
            compressed_size_bytes=compressed_size,
            compression_ratio=round(compression_ratio, 4),
            savings_percent=round(savings_percent, 2),
            content_type=content_type,
            download_url=f"/api/v1/compression/download/{output_path.name}",
        )

    async def compress_batch(
        self,
        files: list[UploadFile],
        image_output_format: str = "webp",
        compression_preset: str = "balanced",
        max_dimension: int | None = None,
    ) -> BatchCompressionResult:
        if not files:
            raise HTTPException(status_code=400, detail="No files were uploaded.")
        if len(files) > 20:
            raise HTTPException(status_code=400, detail="You can process a maximum of 20 files at once.")

        job_id = job_service.create([file.filename or "file" for file in files])
        job_service.update_status(job_id, "processing")

        results: list[CompressionResult] = []
        archive_files: list[tuple[str, bytes]] = []
        total_original_size = 0
        total_compressed_size = 0

        try:
            for file in files:
                try:
                    file_data = await file.read()
                    inspection = inspect_and_validate(file_data)
                    original_size = len(file_data)

                    if inspection.category.value == "image":
                        compressed_data, content_type, _quality, _width, _height = (
                            compression_service.compress_image(
                                file_data=file_data,
                                preset=compression_preset,
                                output_format=image_output_format,
                                max_dimension=max_dimension,
                            )
                        )
                        extension = {"webp": "webp", "jpeg": "jpg", "png": "png"}.get(
                            image_output_format,
                            "webp",
                        )
                    elif inspection.category.value == "pdf":
                        compressed_data, content_type, _pdf_quality = compression_service.compress_pdf(
                            file_data=file_data,
                            preset=compression_preset,
                        )
                        extension = "pdf"
                    else:
                        raise HTTPException(status_code=415, detail="Unsupported file type.")

                    if len(compressed_data) >= original_size:
                        compressed_data = file_data
                        compressed_size = original_size
                        content_type = inspection.mime_type
                        extension = (Path(file.filename or "").suffix.lower().lstrip("."))
                    else:
                        compressed_size = len(compressed_data)

                    output_filename = generate_filename(file.filename or "file", extension=extension)
                    output_path = compression_repository.save(compressed_data, output_filename)
                    savings_percent = ((1 - (compressed_size / original_size)) * 100) if original_size else 0

                    result = CompressionResult(
                        success=True,
                        original_filename=file.filename or "file",
                        output_filename=output_path.name,
                        original_size_bytes=original_size,
                        compressed_size_bytes=compressed_size,
                        compression_ratio=round(compressed_size / original_size, 4) if original_size else 0,
                        savings_percent=round(savings_percent, 2),
                        content_type=content_type,
                        download_url=f"/api/v1/compression/download/{output_path.name}",
                    )
                    results.append(result)
                    archive_files.append((output_path.name, compressed_data))
                    total_original_size += original_size
                    total_compressed_size += compressed_size
                except HTTPException:
                    results.append(
                        CompressionResult(
                            success=False,
                            original_filename=file.filename or "file",
                            output_filename="",
                            original_size_bytes=0,
                            compressed_size_bytes=0,
                            compression_ratio=0,
                            savings_percent=0,
                            content_type="",
                            download_url="",
                        )
                    )

            successful_files = len(archive_files)
            failed_files = len(files) - successful_files
            if successful_files == 0:
                raise HTTPException(status_code=422, detail="None of the uploaded files could be processed.")

            archive_filename = f"compressed_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            archive_data = archive_service.create_zip(archive_files)
            compression_repository.save(archive_data, archive_filename)

            overall_savings = (
                (1 - (total_compressed_size / total_original_size)) * 100
                if total_original_size
                else 0
            )

            job_service.update_status(job_id, "completed")
            return BatchCompressionResult(
                success=True,
                total_files=len(files),
                successful_files=successful_files,
                failed_files=failed_files,
                original_size_bytes=total_original_size,
                compressed_size_bytes=total_compressed_size,
                savings_percent=round(overall_savings, 2),
                files=results,
                download_all_url=f"/api/v1/compression/download/{archive_filename}",
            )
        except Exception as error:
            logger.exception(
                "Failed to finalize batch compression job %s: %s",
                job_id,
                error,
            )
            job_service.update_status(job_id, "failed")
            raise


compression_controller = CompressionController()
