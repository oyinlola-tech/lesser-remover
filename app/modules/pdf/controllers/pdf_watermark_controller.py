"""PDF watermarking controller."""

from fastapi import HTTPException, UploadFile

from app.modules.pdf.controllers.pdf_controller_helpers import (
    read_pdf,
    save_output,
)
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)
from app.modules.pdf.pdf_service import pdf_service


class PdfWatermarkController:

    async def watermark(
        self,
        file: UploadFile,
        text: str = "CONFIDENTIAL",
    ) -> PdfToolResponse:
        file_data, filename = await read_pdf(file)
        try:
            data, page_count = pdf_service.add_watermark(file_data, text)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        return save_output(data, f"watermarked_{filename}", {"page_count": page_count})


pdf_watermark_controller = PdfWatermarkController()
