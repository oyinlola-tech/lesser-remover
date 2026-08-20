"""PDF info controller."""

from fastapi import HTTPException, UploadFile

from app.modules.pdf.controllers.pdf_controller_helpers import (
    read_pdf,
)
from app.modules.pdf.pdf_schema import (
    PdfInfoResponse,
)
from app.modules.pdf.pdf_service import pdf_service


class PdfInfoController:

    async def info(
        self,
        file: UploadFile,
    ) -> PdfInfoResponse:
        file_data, filename = await read_pdf(file)
        try:
            page_count = pdf_service.page_count(file_data)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to read PDF: {error}",
            ) from error
        return PdfInfoResponse(
            success=True,
            filename=filename,
            page_count=page_count,
            file_size_bytes=len(file_data),
        )


pdf_info_controller = PdfInfoController()
