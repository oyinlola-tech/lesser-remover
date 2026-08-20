"""PDF page extraction controller."""

from fastapi import HTTPException, UploadFile

from app.modules.pdf.controllers.pdf_controller_helpers import (
    read_pdf,
    save_output,
)
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)
from app.modules.pdf.pdf_service import pdf_service


class PdfExtractController:

    async def extract_pages(
        self,
        file: UploadFile,
        pages_spec: str,
    ) -> PdfToolResponse:
        file_data, filename = await read_pdf(file)
        try:
            data, entries = pdf_service.extract_pages(
                file_data,
                pages_spec,
                filename,
            )
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to extract pages: {error}",
            ) from error
        base_name = filename.rsplit(".", 1)[0]
        return save_output(
            data,
            f"{base_name}-extracted.zip",
            {"page_count": len(entries)},
        )


pdf_extract_controller = PdfExtractController()
