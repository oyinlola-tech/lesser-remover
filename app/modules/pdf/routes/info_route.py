"""PDF info route."""

import logging

from fastapi import APIRouter, File, UploadFile

from app.api import API_PREFIX
from app.modules.pdf.pdf_controller import pdf_controller
from app.modules.pdf.pdf_schema import (
    PdfInfoResponse,
)

logger = logging.getLogger(__name__)


def create_info_router() -> APIRouter:
    router = APIRouter(
        prefix=f"{API_PREFIX}/tools/pdf",
        tags=["PDF Tools"],
    )

    @router.post("/info", response_model=PdfInfoResponse)
    async def pdf_info(
        file: UploadFile = File(...),
    ):
        logger.info("pdf_info: file=%s", file.filename)
        return await pdf_controller.info(file)

    return router
