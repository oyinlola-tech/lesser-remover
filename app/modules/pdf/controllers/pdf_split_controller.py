"""PDF split controller."""

from fastapi import HTTPException, UploadFile

from app.modules.pdf.controllers.pdf_controller_helpers import (
    read_pdf,
    save_output,
)
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)
from app.modules.pdf.pdf_service import pdf_service


class PdfSplitController:

    async def split(
        self,
        file: UploadFile,
    ) -> PdfToolResponse:
        file_data, filename = await read_pdf(file)
        try:
            data, entries = pdf_service.split(file_data, filename)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to split PDF: {error}",
            ) from error
        base_name = filename.rsplit(".", 1)[0]
        return save_output(
            data,
            f"{base_name}-split.zip",
            {"page_count": len(entries)},
        )


pdf_split_controller = PdfSplitController()
