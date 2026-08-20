"""Shared PDF controller helpers."""

from fastapi import HTTPException, UploadFile

from app.modules.pdf.pdf_repository import pdf_repository
from app.modules.pdf.pdf_schema import (
    PdfToolResponse,
)
from app.shared.file_inspection.file_validation import (
    inspect_and_validate,
)


async def read_pdf(
    file: UploadFile,
) -> tuple[bytes, str]:
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
    if inspection.category.value != "pdf":
        raise HTTPException(
            status_code=415,
            detail="Only PDF files are supported",
        )
    return file_data, file.filename


def save_output(
    data: bytes,
    filename: str,
    details: dict | None = None,
) -> PdfToolResponse:
    output_path = pdf_repository.save_output_file(
        data,
        filename,
    )
    return PdfToolResponse(
        success=True,
        filename=output_path.name,
        size_bytes=len(data),
        download_url=f"/api/v1/tools/pdf/download/{output_path.name}",
        details=details or {},
    )


def http_error(action: str):
    def raise_error(error: Exception) -> None:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to {action}: {error}",
        ) from error

    return raise_error
