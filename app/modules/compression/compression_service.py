"""Facade over the image-compressor and pdf-compressor services."""

import logging
import time
from io import BytesIO

from app.core.logging import get_tool_logger
from app.modules.compression.image_compression.image_compression_service import (
    image_compression_service,
)
from app.modules.compression.pdf_compression.pdf_compression_service import (
    pdf_compression_service,
)

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_FORMATS = {"webp", "jpeg", "png"}


class CompressionService:
    """Delegates compression to the per-tool compression services."""

    def compress_image(
        self,
        file_data: bytes,
        preset: str = "balanced",
        output_format: str = "webp",
        target_size_bytes: int | None = None,
        max_dimension: int | None = None,
        strip_metadata: bool = True,
    ) -> tuple[bytes, str, int, int, int]:
        tool_logger = get_tool_logger("image-compressor")
        started = time.monotonic()
        actual_format = self._resolve_output_format(file_data, output_format)

        if target_size_bytes is not None:
            result = image_compression_service.compress_to_target(
                file_data=file_data,
                target_size_bytes=target_size_bytes,
                output_format=actual_format,
                max_dimension=max_dimension,
                strip_metadata=strip_metadata,
            )
            tool_logger.info(
                "compressed image to target %d bytes (%d -> %d bytes, %s) in %.2fs",
                target_size_bytes, len(file_data), len(result[0]),
                actual_format, time.monotonic() - started,
            )
            return result

        result = image_compression_service.compress_with_preset(
            file_data=file_data,
            preset=preset,
            output_format=actual_format,
            max_dimension=max_dimension,
            strip_metadata=strip_metadata,
        )
        tool_logger.info(
            "compressed image with preset %s (%d -> %d bytes, %s) in %.2fs",
            preset, len(file_data), len(result[0]),
            actual_format, time.monotonic() - started,
        )
        return result

    def compress_image_quality(
        self,
        file_data: bytes,
        quality: int,
        output_format: str = "webp",
        target_size_bytes: int | None = None,
        max_dimension: int | None = None,
        strip_metadata: bool = True,
    ) -> tuple[bytes, str, int, int, int]:
        tool_logger = get_tool_logger("image-compressor")
        started = time.monotonic()
        actual_format = self._resolve_output_format(file_data, output_format)

        if target_size_bytes is not None:
            result = image_compression_service.compress_to_target(
                file_data=file_data,
                target_size_bytes=target_size_bytes,
                output_format=actual_format,
                max_dimension=max_dimension,
                strip_metadata=strip_metadata,
            )
            tool_logger.info(
                "compressed image to target %d bytes (q%d, %d -> %d bytes, %s) in %.2fs",
                target_size_bytes, quality, len(file_data), len(result[0]),
                actual_format, time.monotonic() - started,
            )
            return result

        result = image_compression_service.compress(
            file_data=file_data,
            output_format=actual_format,
            quality=quality,
            max_dimension=max_dimension,
            strip_metadata=strip_metadata,
        )
        tool_logger.info(
            "compressed image at quality %d (%d -> %d bytes, %s) in %.2fs",
            quality, len(file_data), len(result[0]),
            actual_format, time.monotonic() - started,
        )
        return result

    def compress_pdf(
        self,
        file_data: bytes,
        preset: str = "balanced",
    ) -> tuple[bytes, str, str]:
        tool_logger = get_tool_logger("pdf-compressor")
        started = time.monotonic()
        data, quality = pdf_compression_service.compress_best(
            file_data=file_data,
            preset=preset,
        )
        tool_logger.info(
            "compressed pdf with preset %s (%d -> %d bytes) in %.2fs",
            preset, len(file_data), len(data),
            time.monotonic() - started,
        )
        return data, "application/pdf", quality

    @staticmethod
    def _resolve_output_format(
        file_data: bytes,
        output_format: str,
    ) -> str:
        """Resolve ``auto`` to the source image format when detected."""
        if output_format.lower() != "auto":
            return output_format
        from PIL import Image

        try:
            source_image = Image.open(BytesIO(file_data))
            source_format = (source_image.format or "webp").lower()
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


compression_service = CompressionService()
