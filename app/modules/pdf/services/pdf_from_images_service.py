"""Images to PDF conversion service."""

import time
from io import BytesIO

from PIL import Image

from app.core.logging import get_tool_logger


class PdfFromImagesService:

    def from_images(
        self,
        images: list[tuple[str, bytes]],
    ) -> tuple[bytes, int]:
        tool_logger = get_tool_logger("image-to-pdf")
        started = time.monotonic()
        if not images:
            raise ValueError("No images were provided.")
        first = Image.open(BytesIO(images[0][1]))
        first.load()
        if first.mode in ("RGBA", "LA", "P"):
            first = first.convert("RGB")
        pages = [first]
        for _, data in images[1:]:
            image = Image.open(BytesIO(data))
            image.load()
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGB")
            pages.append(image)
        output_buffer = BytesIO()
        pages[0].save(
            output_buffer,
            format="PDF",
            save_all=True,
            append_images=pages[1:],
            resolution=150,
        )
        data = output_buffer.getvalue()
        tool_logger.info(
            "created PDF from %d images (%d bytes) in %.2fs",
            len(pages),
            len(data),
            time.monotonic() - started,
        )
        return data, len(pages)


pdf_from_images_service = PdfFromImagesService()
