"""PDF merge route."""

import logging

from fastapi import APIRouter, File, UploadFile

from app.api import API_PREFIX
from app.modules.pdf.pdf_controller import pdf_controller
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)

logger = logging.getLogger(__name__)


def create_merge_router() -> APIRouter:
    router = APIRouter(
        prefix=f"{API_PREFIX}/tools/pdf",
        tags=["PDF Tools"],
    )

    @router.post("/merge", response_model=PdfToolResponse)
    async def merge_pdfs(
        files: list[UploadFile] = File(...),
    ):
        logger.info("merge_pdfs: files=%d", len(files))
        return await pdf_controller.merge(files)

    return router
