"""Facade over the pure-Python PDF toolkit.

PDF compression and PDF-to-image rendering previously depended on the
Ghostscript binary, which serverless runtimes such as Vercel cannot
provide. PyMuPDF ships as a self-contained wheel, so both operations
now run in any environment.
"""

from typing import ClassVar

from app.infrastructure.compression.ghostscript_compress import (
    compress_pdf,
)
from app.infrastructure.compression.ghostscript_render import (
    render_pages,
)


class GhostscriptAdapter:
    """Compress and rasterize PDFs without external binaries."""

    QUALITY_SETTINGS: ClassVar[dict[str, int]] = {
        "screen": 55,
        "ebook": 65,
        "printer": 78,
        "prepress": 88,
        "default": 65,
    }

    def compress(
        self,
        file_data: bytes,
        quality: str = "ebook",
    ) -> bytes:
        return compress_pdf(file_data, quality=quality)

    def to_images(
        self,
        file_data: bytes,
        image_format: str = "png",
        dpi: int = 150,
    ) -> list[tuple[str, bytes]]:
        return render_pages(
            file_data,
            image_format=image_format,
            dpi=dpi,
        )


ghostscript_adapter = GhostscriptAdapter()
