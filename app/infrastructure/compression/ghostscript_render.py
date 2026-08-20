"""PDF-to-image rendering via PyMuPDF pixmaps."""

from app.infrastructure.compression.ghostscript_utils import (
    get_pymupdf,
)


def render_pages(
    file_data: bytes,
    image_format: str = "png",
    dpi: int = 150,
) -> list[tuple[str, bytes]]:
    image_format = image_format.lower()
    if image_format not in {"png", "jpeg"}:
        raise ValueError(
            "Image format must be png or jpeg."
        )
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
