"""Image conversion logic for the image-converter tool."""

import time

from app.core.logging import get_tool_logger
from app.infrastructure.compression.pillow_adapter import pillow_adapter
from app.modules.image.services.image_helpers import (
    SUPPORTED_CONVERSION_FORMATS,
    has_transparency,
    is_animated,
    open_image,
    prepare_for_output,
)


class ImageConverterService:
    """Convert an image between jpg, png, webp and avif."""

    def convert(
        self,
        file_data: bytes,
        output_format: str,
        quality: int | None = None,
        strip_metadata: bool = True,
        background_color: str | None = None,
        lossless: bool = False,
    ) -> dict:
        """Convert an image to another format.

        Returns encoded bytes plus metadata about the conversion,
        including whether transparency was flattened.
        """
        tool_logger = get_tool_logger("image-converter")
        started = time.monotonic()
        output_format = output_format.lower()
        if output_format not in SUPPORTED_CONVERSION_FORMATS:
            raise ValueError(
                f"Unsupported output format: {output_format}. "
                "Use jpg, png, webp or avif."
            )

        image = open_image(file_data)
        input_format = (image.format or "unknown").upper()

        if is_animated(image):
            raise ValueError("Animated images are not supported for conversion.")

        original_size = len(file_data)
        original_width = image.width
        original_height = image.height

        image, flattened = prepare_for_output(
            image,
            output_format,
            background_color,
        )

        if output_format in ("jpg", "jpeg") and quality is None:
            quality = 90
        elif output_format == "webp" and quality is None:
            quality = 95

        data, content_type = pillow_adapter.encode(
            image,
            output_format,
            quality=quality or 92,
            strip_metadata=strip_metadata,
            lossless=lossless,
            background_color=background_color,
        )

        tool_logger.info(
            "converted %s -> %s (%dx%d, %d -> %d bytes) in %.2fs",
            input_format,
            output_format,
            original_width,
            original_height,
            original_size,
            len(data),
            time.monotonic() - started,
        )
        return {
            "data": data,
            "content_type": content_type,
            "extension": "jpg" if output_format in ("jpg", "jpeg") else output_format,
            "width": image.width,
            "height": image.height,
            "input_format": input_format,
            "original_width": original_width,
            "original_height": original_height,
            "original_size": original_size,
            "output_size": len(data),
            "flattened": flattened,
            "has_alpha": has_transparency(image) if not flattened else False,
        }


image_converter_service = ImageConverterService()
