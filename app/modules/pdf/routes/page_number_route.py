"""PDF page-numbering route."""

from fastapi import APIRouter, File, Form, UploadFile

from app.api import API_PREFIX
from app.modules.pdf.pdf_controller import pdf_controller
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)


def create_page_number_router() -> APIRouter:
    router = APIRouter(
        prefix=f"{API_PREFIX}/tools/pdf",
        tags=["PDF Tools"],
    )

    @router.post("/page-number", response_model=PdfToolResponse)
    async def page_number_pdf(
        file: UploadFile = File(...),
        position: str = Form("bottom-right"),
    ):
        return await pdf_controller.page_number(file, position=position)

    return router
