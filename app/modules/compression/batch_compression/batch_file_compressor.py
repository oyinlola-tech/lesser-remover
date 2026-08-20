"""Pure per-file compression selection for batch jobs."""

from dataclasses import dataclass

from app.modules.compression.compression_service import (
    compression_service,
)


@dataclass
class CompressionResult:
    data: bytes
    content_type: str
    extension: str
    quality: int | None = None
    compression_preset: str | None = None
    width: int | None = None
    height: int | None = None


class BatchFileCompressor:

    def compress_file(
        self,
        file_data: bytes,
        inspection,
        image_output_format: str,
        compression_preset: str,
        target_size_bytes: int | None = None,
        max_dimension: int | None = None,
        strip_metadata: bool = True,
        quality: int | None = None,
    ) -> CompressionResult:

        if inspection.category.value == "image":
            return self._compress_image(
                file_data=file_data,
                inspection=inspection,
                image_output_format=image_output_format,
                compression_preset=compression_preset,
                target_size_bytes=target_size_bytes,
                max_dimension=max_dimension,
                strip_metadata=strip_metadata,
                quality=quality,
            )

        if inspection.category.value == "pdf":
            return self._compress_pdf(
                file_data=file_data,
                compression_preset=compression_preset,
            )

        raise ValueError("Unsupported file type.")

    @staticmethod
    def _compress_image(
        file_data: bytes,
        inspection,
        image_output_format: str,
        compression_preset: str,
        target_size_bytes: int | None,
        max_dimension: int | None,
        strip_metadata: bool,
        quality: int | None,
    ) -> CompressionResult:

        if quality is not None:
            data, content_type, actual_quality, width, height = (
                compression_service.compress_image_quality(
                    file_data=file_data,
                    quality=quality,
                    output_format=image_output_format,
                    max_dimension=max_dimension,
                    target_size_bytes=target_size_bytes,
                    strip_metadata=strip_metadata,
                )
            )
        else:
            data, content_type, actual_quality, width, height = (
                compression_service.compress_image(
                    file_data=file_data,
                    preset=compression_preset,
                    output_format=image_output_format,
                    max_dimension=max_dimension,
                    target_size_bytes=target_size_bytes,
                    strip_metadata=strip_metadata,
                )
            )

        extension = BatchFileCompressor._resolve_extension(
            image_output_format,
            inspection.extension,
        )

        return CompressionResult(
            data=data,
            content_type=content_type,
            extension=extension,
            quality=actual_quality,
            compression_preset=compression_preset,
            width=width,
            height=height,
        )

    @staticmethod
    def _compress_pdf(
        file_data: bytes,
        compression_preset: str,
    ) -> CompressionResult:

        data, content_type, actual_preset = (
            compression_service.compress_pdf(
                file_data=file_data,
                preset=compression_preset,
            )
        )

        return CompressionResult(
            data=data,
            content_type=content_type,
            extension="pdf",
            compression_preset=actual_preset,
        )

    @staticmethod
    def _resolve_extension(
        image_output_format: str,
        source_extension: str,
    ) -> str:
        mapped = {
            "webp": "webp",
            "jpeg": "jpg",
            "jpg": "jpg",
            "png": "png",
        }.get(image_output_format)
        if mapped:
            return mapped
        if source_extension in (".jpg", ".jpeg"):
            return "jpg"
        if source_extension == ".webp":
            return "webp"
        if source_extension == ".png":
            return "png"
        return "webp"


batch_file_compressor = BatchFileCompressor()
