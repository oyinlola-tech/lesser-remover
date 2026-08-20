"""Metadata stripping logic for the metadata-remover tool."""

import time

from app.core.logging import get_tool_logger
from app.infrastructure.compression.pillow_adapter import pillow_adapter
from app.modules.image.services.image_helpers import open_image


class MetadataRemoverService:
    """Re-encode images without EXIF/GPS/camera metadata."""

    def remove_metadata(self, file_data: bytes) -> dict:
        """Re-encode the image, dropping EXIF/GPS/camera metadata.

        Explicit operation: callers only invoke it when the user asked
        for metadata removal.
        """
        tool_logger = get_tool_logger("metadata-remover")
        started = time.monotonic()
        image = open_image(file_data)
        source_format = (image.format or "png").upper()
        removed = [
            key
            for key in (
                "exif",
                "gps",
                "dpi",
                "icc_profile",
                "comment",
                "photoshop",
            )
            if key in image.info
        ]
        if source_format == "JPEG":
            data = pillow_adapter.encode_jpeg(image, quality=95)
            content_type = "image/jpeg"
            extension = "jpg"
        elif source_format == "WEBP":
            data = pillow_adapter.encode_webp(image, quality=95)
            content_type = "image/webp"
            extension = "webp"
        elif source_format == "PNG":
            data = pillow_adapter.encode_png(image)
            content_type = "image/png"
            extension = "png"
        else:
            data = pillow_adapter.encode_png(image.convert("RGBA"))
            content_type = "image/png"
            extension = "png"
        tool_logger.info(
            "stripped metadata %s from %s (%d bytes) in %.2fs",
            removed,
            source_format,
            len(data),
            time.monotonic() - started,
        )
        return {
            "data": data,
            "content_type": content_type,
            "extension": extension,
            "removed_metadata": removed,
            "width": image.width,
            "height": image.height,
            "input_format": source_format,
            "original_size": len(file_data),
            "output_size": len(data),
        }


metadata_remover_service = MetadataRemoverService()
