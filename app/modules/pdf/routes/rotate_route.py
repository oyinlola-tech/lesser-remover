"""PDF rotate route."""

import logging

from fastapi import APIRouter, File, Form, UploadFile

from app.api import API_PREFIX
from app.modules.pdf.pdf_controller import pdf_controller
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)

logger = logging.getLogger(__name__)


def create_rotate_router() -> APIRouter:
    router = APIRouter(
        prefix=f"{API_PREFIX}/tools/pdf",
        tags=["PDF Tools"],
    )

    @router.post("/rotate", response_model=PdfToolResponse)
    async def rotate_pdf(
        file: UploadFile = File(...),
        angle: int = Form(90),
        pages: str = Form("all"),
    ):
        logger.info("rotate_pdf: file=%s angle=%d pages=%s", file.filename, angle, pages)
        return await pdf_controller.rotate(
            file,
            angle=angle,
            pages_spec=pages,
        )

    return router
