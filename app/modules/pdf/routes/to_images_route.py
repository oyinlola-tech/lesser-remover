"""PDF to images conversion route."""

import logging

from fastapi import APIRouter, File, Form, UploadFile

from app.api import API_PREFIX
from app.modules.pdf.pdf_controller import pdf_controller
from app.modules.pdf.pdf_schema import (
    PdfImagesResponse,
)
from app.modules.pdf.routes.pdf_route_helpers import (
    check_pdf_to_image_capability,
)

logger = logging.getLogger(__name__)


def create_to_images_router() -> APIRouter:
    router = APIRouter(
        prefix=f"{API_PREFIX}/tools/pdf",
        tags=["PDF Tools"],
    )

    @router.post("/to-images", response_model=PdfImagesResponse)
    async def pdf_to_images(
        file: UploadFile = File(...),
        image_format: str = Form("png"),
        dpi: int = Form(150),
        as_zip: bool = Form(False),
    ):
        check_pdf_to_image_capability()
        logger.info(
            "pdf_to_images: file=%s format=%s dpi=%d as_zip=%s",
            file.filename,
            image_format,
            dpi,
            as_zip,
        )
        return await pdf_controller.to_images(
            file,
            image_format=image_format,
            dpi=dpi,
            as_zip=as_zip,
        )

    return router
