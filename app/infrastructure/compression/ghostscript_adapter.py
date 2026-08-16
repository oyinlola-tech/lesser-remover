"""Pure-Python PDF toolkit built on PyMuPDF.

PDF compression and PDF-to-image rendering previously depended on the
Ghostscript binary, which serverless runtimes such as Vercel cannot
provide. PyMuPDF ships as a self-contained wheel, so both operations
now run in any environment.
"""

import io
import logging
from typing import TYPE_CHECKING, ClassVar

from PIL import Image

if TYPE_CHECKING:
    import pymupdf

logger = logging.getLogger(__name__)


def _get_pymupdf() -> "pymupdf":
    """Import PyMuPDF lazily so the app boots when it is not installed.

    The module is imported on first use rather than at startup so the
    rest of the API stays available (and PDF tools report themselves as
    unavailable) on runtimes such as Vercel that cannot install it.
    """
    try:
        import pymupdf
    except ImportError as error:
        raise RuntimeError(
            "PyMuPDF is required for PDF compression and "
            "PDF-to-image conversion but is not installed."
        ) from error
    return pymupdf


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
        if quality not in self.QUALITY_SETTINGS:
            raise ValueError(
                f"Unsupported PDF quality: {quality}"
            )
        jpeg_quality = self.QUALITY_SETTINGS[quality]
        pymupdf = _get_pymupdf()
        try:
            document = pymupdf.open(
                stream=file_data,
                filetype="pdf",
            )
        except Exception as error:
            raise RuntimeError(
                f"Unable to open PDF: {error}"
            ) from error
        try:
            for page in document:
                for image_info in page.get_images(full=True):
                    xref = image_info[0]
                    smask = image_info[1]
                    if smask:
                        continue
                    try:
                        extracted = document.extract_image(xref)
                    except Exception as error:
                        logger.debug(
                            "Failed to extract image xref %s: %s",
                            xref,
                            error,
                        )
                        continue
                    if extracted.get("ext") != "jpeg":
                        continue
                    try:
                        image = Image.open(
                            io.BytesIO(extracted["image"])
                        )
                        if image.mode not in ("RGB", "L"):
                            image = image.convert("RGB")
                        buffer = io.BytesIO()
                        image.save(
                            buffer,
                            "JPEG",
                            quality=jpeg_quality,
                            optimize=True,
                            progressive=True,
                        )
                    except Exception as error:
                        logger.debug(
                            "Failed to process extracted image: %s",
                            error,
                        )
                        continue
                    recompressed = buffer.getvalue()
                    if len(recompressed) >= len(
                        extracted["image"]
                    ):
                        continue
                    document.update_stream(
                        xref,
                        recompressed,
                    )
                    document.xref_set_key(
                        xref,
                        "DecodeParms",
                        "null",
                    )
            output = io.BytesIO()
            document.save(
                output,
                garbage=4,
                deflate=True,
                clean=True,
            )
            data = output.getvalue()
        finally:
            document.close()
        return data

    def to_images(
        self,
        file_data: bytes,
        image_format: str = "png",
        dpi: int = 150,
    ) -> list[tuple[str, bytes]]:
        image_format = image_format.lower()
        if image_format not in {"png", "jpeg"}:
            raise ValueError(
                "Image format must be png or jpeg."
            )
        pymupdf = _get_pymupdf()
        try:
            document = pymupdf.open(
                stream=file_data,
                filetype="pdf",
            )
        except Exception as error:
            raise RuntimeError(
                f"Unable to open PDF: {error}"
            ) from error
        try:
            pages: list[tuple[str, bytes]] = []
            for index, page in enumerate(
                document,
                start=1,
            ):
                pixmap = page.get_pixmap(
                    dpi=dpi,
                    colorspace=pymupdf.csRGB,
                    alpha=False,
                )
                if image_format == "png":
                    data = pixmap.tobytes("png")
                    extension = "png"
                else:
                    data = pixmap.tobytes(
                        "jpeg",
                        jpg_quality=90,
                    )
                    extension = "jpg"
                pages.append(
                    (
                        f"page-{index:03d}.{extension}",
                        data,
                    )
                )
        finally:
            document.close()
        if not pages:
            raise RuntimeError(
                "PDF to image conversion produced no pages."
            )
        return pages


ghostscript_adapter = GhostscriptAdapter()
