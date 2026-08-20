"""PDF compression via PyMuPDF image re-encoding."""

import io
import logging

from PIL import Image

from app.infrastructure.compression.ghostscript_utils import (
    get_pymupdf,
)

logger = logging.getLogger(__name__)

QUALITY_SETTINGS = {
    "screen": 55,
    "ebook": 65,
    "printer": 78,
    "prepress": 88,
    "default": 65,
}


def compress_pdf(
    file_data: bytes,
    quality: str = "ebook",
) -> bytes:
    if quality not in QUALITY_SETTINGS:
        raise ValueError(
            f"Unsupported PDF quality: {quality}"
        )
    jpeg_quality = QUALITY_SETTINGS[quality]
    pymupdf = get_pymupdf()
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
                if len(recompressed) >= len(extracted["image"]):
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
