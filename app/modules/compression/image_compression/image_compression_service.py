"""Facade over the per-tool image compression services."""

from app.modules.compression.image_compression.preset_compression import (
    preset_compression_service,
)
from app.modules.compression.image_compression.quality_compression import (
    quality_compression_service,
)
from app.modules.compression.image_compression.target_compression import (
    target_compression_service,
)


class ImageCompressionService:

    def compress(
        self,
        file_data: bytes,
        output_format: str = "webp",
        quality: int = 85,
        max_dimension: int | None = None,
        strip_metadata: bool = True,
    ) -> tuple[bytes, str, int, int, int]:
        return quality_compression_service.compress(
            file_data=file_data,
            output_format=output_format,
            quality=quality,
            max_dimension=max_dimension,
            strip_metadata=strip_metadata,
        )

    def compress_with_preset(
        self,
        file_data: bytes,
        preset: str = "balanced",
        output_format: str = "webp",
        max_dimension: int | None = None,
        strip_metadata: bool = True,
    ) -> tuple[bytes, str, int, int, int]:
        return preset_compression_service.compress_with_preset(
            file_data=file_data,
            preset=preset,
            output_format=output_format,
            max_dimension=max_dimension,
            strip_metadata=strip_metadata,
        )

    def compress_to_target(
        self,
        file_data: bytes,
        target_size_bytes: int,
        output_format: str = "webp",
        max_dimension: int | None = None,
        strip_metadata: bool = True,
    ) -> tuple[bytes, str, int, int, int]:
        return target_compression_service.compress_to_target(
            file_data=file_data,
            target_size_bytes=target_size_bytes,
            output_format=output_format,
            max_dimension=max_dimension,
            strip_metadata=strip_metadata,
        )


image_compression_service = ImageCompressionService()
