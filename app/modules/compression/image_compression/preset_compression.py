"""Preset-based image compression that picks the best quality level."""

from app.modules.compression.image_compression.image_compression_helpers import (
    encode,
    get_preset,
    prepare_image,
)


class PresetCompressionService:

    def compress_with_preset(
        self,
        file_data: bytes,
        preset: str = "balanced",
        output_format: str = "webp",
        max_dimension: int | None = None,
        strip_metadata: bool = True,
    ) -> tuple[bytes, str, int, int, int]:

        settings = get_preset(preset)

        image = prepare_image(
            file_data,
            max_dimension,
            strip_metadata,
        )

        best_data: bytes | None = None
        best_content_type = ""
        best_quality = 0

        for quality in settings.qualities:

            data, content_type = encode(
                image,
                output_format,
                quality,
                strip_metadata=strip_metadata,
            )

            if best_data is None or len(data) < len(best_data):
                best_data = data
                best_content_type = content_type
                best_quality = quality

        if best_data is None:
            raise RuntimeError("Unable to compress image.")

        return (
            best_data,
            best_content_type,
            best_quality,
            image.width,
            image.height,
        )


preset_compression_service = PresetCompressionService()
