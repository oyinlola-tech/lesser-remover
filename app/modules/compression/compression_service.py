import logging
from io import BytesIO

from app.modules.compression.image_compression.image_compression_service import (
    image_compression_service,
)
from app.modules.compression.pdf_compression.pdf_compression_service import (
    pdf_compression_service,
)

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_FORMATS = {"webp", "jpeg", "png"}


class CompressionService:

    def compress_image(
        self,
        file_data: bytes,
        preset: str = "balanced",
        output_format: str = "webp",
        target_size_bytes: int | None = None,
        max_dimension: int | None = None,
        strip_metadata: bool = True,
    ) -> tuple[bytes, str, int, int, int]:

        actual_format = self._resolve_output_format(
            file_data,
            output_format,
        )

        if target_size_bytes is not None:

            return (
                image_compression_service
                .compress_to_target(
                    file_data=file_data,
                    target_size_bytes=target_size_bytes,
                    output_format=actual_format,
                    max_dimension=max_dimension,
                    strip_metadata=strip_metadata,
                )
            )

        return (
            image_compression_service
            .compress_with_preset(
                file_data=file_data,
                preset=preset,
                output_format=actual_format,
                max_dimension=max_dimension,
                strip_metadata=strip_metadata,
            )
        )

    def compress_image_quality(
        self,
        file_data: bytes,
        quality: int,
        output_format: str = "webp",
        target_size_bytes: int | None = None,
        max_dimension: int | None = None,
        strip_metadata: bool = True,
    ) -> tuple[bytes, str, int, int, int]:

        actual_format = self._resolve_output_format(
            file_data,
            output_format,
        )

        if target_size_bytes is not None:

            return (
                image_compression_service
                .compress_to_target(
                    file_data=file_data,
                    target_size_bytes=target_size_bytes,
                    output_format=actual_format,
                    max_dimension=max_dimension,
                    strip_metadata=strip_metadata,
                )
            )

        return (
            image_compression_service
            .compress(
                file_data=file_data,
                output_format=actual_format,
                quality=quality,
                max_dimension=max_dimension,
                strip_metadata=strip_metadata,
            )
        )

    @staticmethod
    def _resolve_output_format(
        file_data: bytes,
        output_format: str,
    ) -> str:
        """Resolve ``auto`` to the source image format when detected."""
        if output_format.lower() == "auto":
            from PIL import Image

            try:
                source_image = Image.open(BytesIO(file_data))
                source_format = (
                    source_image.format or "webp"
                ).lower()
                source_image.close()
            except Exception as error:
                logger.debug(
                    "Failed to detect source image format, defaulting to webp: %s",
                    error,
                )
                source_format = "webp"
            if source_format not in SUPPORTED_IMAGE_FORMATS:
                source_format = "webp"
            return source_format
        return output_format

    def compress_pdf(
        self,
        file_data: bytes,
        preset: str = "balanced",
    ) -> tuple[bytes, str, str]:

        data, quality = (
            pdf_compression_service.compress_best(
                file_data=file_data,
                preset=preset,
            )
        )

        return (
            data,
            "application/pdf",
            quality,
        )


compression_service = CompressionService()
