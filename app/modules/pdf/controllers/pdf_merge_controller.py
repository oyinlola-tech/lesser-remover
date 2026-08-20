"""PDF merge controller."""

from fastapi import HTTPException, UploadFile

from app.modules.pdf.controllers.pdf_controller_helpers import (
    read_pdf,
    save_output,
)
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)
from app.modules.pdf.pdf_service import pdf_service


class PdfMergeController:

    async def merge(
        self,
        files: list[UploadFile],
    ) -> PdfToolResponse:
        if len(files) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least two PDF files are required to merge.",
            )
        sources: list[tuple[str, bytes]] = []
        for file in files:
            file_data, filename = await read_pdf(file)
            sources.append((filename, file_data))
        try:
            data, page_count = pdf_service.merge(sources)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to merge PDFs: {error}",
            ) from error
        return save_output(
            data,
            "merged.pdf",
            {
                "source_count": len(sources),
                "page_count": page_count,
            },
        )


pdf_merge_controller = PdfMergeController()
