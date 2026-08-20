"""Images to PDF conversion route."""

import logging

from fastapi import APIRouter, File, UploadFile

from app.api import API_PREFIX
from app.modules.pdf.pdf_controller import pdf_controller
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)

logger = logging.getLogger(__name__)


def create_from_images_router() -> APIRouter:
    router = APIRouter(
        prefix=f"{API_PREFIX}/tools/pdf",
        tags=["PDF Tools"],
    )

    @router.post("/from-images", response_model=PdfToolResponse)
    async def images_to_pdf(
        files: list[UploadFile] = File(...),
    ):
        logger.info("images_to_pdf: files=%d", len(files))
        return await pdf_controller.from_images(files)

    return router
