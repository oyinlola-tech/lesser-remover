"""PDF to images conversion service."""

import time

from app.core.logging import get_tool_logger
from app.infrastructure.compression.ghostscript_adapter import (
    ghostscript_adapter,
)


class PdfToImageService:

    def to_images(
        self,
        file_data: bytes,
        image_format: str = "png",
        dpi: int = 150,
    ) -> list[tuple[str, bytes]]:
        tool_logger = get_tool_logger("pdf-to-image")
        started = time.monotonic()
        image_format = image_format.lower()
        if image_format not in {"png", "jpeg"}:
            raise ValueError(
                "Image format must be png or jpeg."
            )
        if dpi < 50 or dpi > 600:
            raise ValueError(
                "DPI must be between 50 and 600."
            )
        pages = ghostscript_adapter.to_images(
            file_data,
            image_format=image_format,
            dpi=dpi,
        )
        tool_logger.info(
            "rendered %d pages as %s at %d dpi in %.2fs",
            len(pages),
            image_format,
            dpi,
            time.monotonic() - started,
        )
        return pages


pdf_to_image_service = PdfToImageService()
