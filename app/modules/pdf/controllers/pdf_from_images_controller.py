"""Images to PDF conversion controller."""

from fastapi import HTTPException, UploadFile

from app.modules.pdf.controllers.pdf_controller_helpers import (
    save_output,
)
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)
from app.modules.pdf.pdf_service import pdf_service
from app.shared.file_inspection.file_validation import (
    inspect_and_validate,
)


class PdfFromImagesController:

    async def from_images(
        self,
        files: list[UploadFile],
    ) -> PdfToolResponse:
        if not files:
            raise HTTPException(
                status_code=400,
                detail="At least one image is required.",
            )
        images: list[tuple[str, bytes]] = []
        for file in files:
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail="Filename is required",
                )
            file_data = await file.read()
            if not file_data:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file is empty",
                )
            inspection = inspect_and_validate(file_data)
            if inspection.category.value != "image":
                raise HTTPException(
                    status_code=415,
                    detail=f"Not an image file: {file.filename}",
                )
            images.append((file.filename, file_data))
        try:
            data, page_count = pdf_service.from_images(images)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to create PDF: {error}",
            ) from error
        return save_output(
            data,
            "images.pdf",
            {"page_count": page_count},
        )


pdf_from_images_controller = PdfFromImagesController()
