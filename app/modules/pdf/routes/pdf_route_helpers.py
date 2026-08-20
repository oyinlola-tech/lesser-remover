"""PDF route helpers."""

from fastapi import HTTPException

from app.core.capabilities import capability_registry


def check_pdf_to_image_capability() -> None:
    if not capability_registry.is_available("pdf-to-image"):
        raise HTTPException(
            status_code=503,
            detail="PDF to image conversion is unavailable in the current environment.",
        )
