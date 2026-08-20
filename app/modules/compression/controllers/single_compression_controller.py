"""Single-file compression controller."""

from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.modules.compression.compression_repository import (
    compression_repository,
)
from app.modules.compression.compression_schema import (
    CompressionResult,
)
from app.modules.compression.compression_service import (
    compression_service,
)
from app.shared.file_inspection.file_validation import (
    inspect_and_validate,
)
from app.shared.utils.file_util import generate_filename


class SingleCompressionController:

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


single_compression_controller = SingleCompressionController()
