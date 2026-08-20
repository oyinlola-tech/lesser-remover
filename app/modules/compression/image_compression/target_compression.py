"""Target-size image compression using a quality binary search."""

from app.modules.compression.image_compression.image_compression_helpers import (
    encode,
    prepare_image,
)


class TargetCompressionService:

    def compress_to_target(
        self,
        file_data: bytes,
        target_size_bytes: int,
        output_format: str = "webp",
        max_dimension: int | None = None,
        strip_metadata: bool = True,
    ) -> tuple[bytes, str, int, int, int]:

        if output_format == "png":
            raise ValueError(
                "Target size compression requires a lossy-capable "
                "format such as WebP or JPEG."
            )

        image = prepare_image(
            file_data,
            max_dimension,
            strip_metadata,
        )

        low = 20
        high = 100

        best_data: bytes | None = None
        best_content_type = ""
        best_quality = 0

        while low <= high:

            quality = (low + high) // 2

            data, content_type = encode(
                image,
                output_format,
                quality,
                strip_metadata=strip_metadata,
            )

            if len(data) <= target_size_bytes:
                best_data = data
                best_content_type = content_type
                best_quality = quality
                low = quality + 1
            else:
                high = quality - 1

        if best_data is None:

            data, content_type = encode(
                image,
                output_format,
                20,
                strip_metadata=strip_metadata,
            )

            return (
                data,
                content_type,
                20,
                image.width,
                image.height,
            )

        return (
            best_data,
            best_content_type,
            best_quality,
            image.width,
            image.height,
        )


target_compression_service = TargetCompressionService()
