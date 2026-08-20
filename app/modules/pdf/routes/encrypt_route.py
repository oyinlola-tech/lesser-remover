"""PDF encryption route."""

from fastapi import APIRouter, File, Form, UploadFile

from app.api import API_PREFIX
from app.modules.pdf.pdf_controller import pdf_controller
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)


def create_encrypt_router() -> APIRouter:
    router = APIRouter(
        prefix=f"{API_PREFIX}/tools/pdf",
        tags=["PDF Tools"],
    )

    @router.post("/encrypt", response_model=PdfToolResponse)
    async def encrypt_pdf(
        file: UploadFile = File(...),
        password: str = Form(...),
        owner_password: str | None = Form(None),
    ):
        return await pdf_controller.encrypt(file, user_password=password, owner_password=owner_password)

    return router
