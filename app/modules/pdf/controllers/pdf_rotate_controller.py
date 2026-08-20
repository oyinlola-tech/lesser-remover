"""PDF rotate controller."""

from fastapi import HTTPException, UploadFile

from app.modules.pdf.controllers.pdf_controller_helpers import (
    read_pdf,
    save_output,
)
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)
from app.modules.pdf.pdf_service import pdf_service


class PdfRotateController:

    async def rotate(
        self,
        file: UploadFile,
        angle: int,
        pages_spec: str,
    ) -> PdfToolResponse:
        file_data, filename = await read_pdf(file)
        try:
            data, page_count = pdf_service.rotate(
                file_data,
                angle,
                pages_spec,
            )
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to rotate PDF: {error}",
            ) from error
        return save_output(
            data,
            f"{filename.rsplit('.', 1)[0]}-rotated.pdf",
            {
                "angle": angle,
                "page_count": page_count,
            },
        )


pdf_rotate_controller = PdfRotateController()
