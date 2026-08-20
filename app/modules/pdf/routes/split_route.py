"""PDF split route."""

import logging

from fastapi import APIRouter, File, UploadFile

from app.api import API_PREFIX
from app.modules.pdf.pdf_controller import pdf_controller
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)

logger = logging.getLogger(__name__)


def create_split_router() -> APIRouter:
    router = APIRouter(
        prefix=f"{API_PREFIX}/tools/pdf",
        tags=["PDF Tools"],
    )

    @router.post("/split", response_model=PdfToolResponse)
    async def split_pdf(
        file: UploadFile = File(...),
    ):
        logger.info("split_pdf: file=%s", file.filename)
        return await pdf_controller.split(file)

    return router
