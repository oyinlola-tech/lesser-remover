"""Quality-based image compression."""

from app.modules.compression.image_compression.image_compression_helpers import (
    encode,
    prepare_image,
)


class QualityCompressionService:

    def compress(
        self,
        file_data: bytes,
        output_format: str = "webp",
        quality: int = 85,
        max_dimension: int | None = None,
        strip_metadata: bool = True,
    ) -> tuple[bytes, str, int, int, int]:

        image = prepare_image(
            file_data,
            max_dimension,
            strip_metadata,
        )

        data, content_type = encode(
            image,
            output_format,
            quality,
            strip_metadata=strip_metadata,
        )

        return data, content_type, quality, image.width, image.height


quality_compression_service = QualityCompressionService()
