from io import BytesIO

from fastapi import HTTPException
from PIL import Image
from PIL import UnidentifiedImageError


Image.MAX_IMAGE_PIXELS = 50_000_000


MAX_IMAGE_SIZE = 25 * 1024 * 1024
MAX_PDF_SIZE = 50 * 1024 * 1024


def validate_file_size(
    file_data: bytes,
    maximum_size: int,
) -> None:
    file_size = len(file_data)
    if file_size > maximum_size:
        maximum_mb = maximum_size / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=(
                f"File is too large. "
                f"Maximum size is "
                f"{maximum_mb:.0f} MB."
            ),
        )


def validate_image(
    file_data: bytes,
) -> Image.Image:
    try:
        image = Image.open(BytesIO(file_data))
        image.verify()
        image = Image.open(BytesIO(file_data))
        image.load()
        return image
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
    ) as error:
        raise ValueError(
            "The uploaded file is not a valid image."
        ) from error


from app.shared.file_inspection.file_inspector import (
    FileInspectionResult,
    file_inspector,
)


def inspect_and_validate(
    file_data: bytes,
) -> FileInspectionResult:
    if not file_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    inspection = file_inspector.inspect(file_data)

    if not inspection.is_supported:
        raise HTTPException(
            status_code=415,
            detail="This file type is not supported.",
        )

    if inspection.category.value == "image":
        validate_file_size(file_data, MAX_IMAGE_SIZE)
        try:
            validate_image(file_data)
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error
    elif inspection.category.value == "pdf":
        validate_file_size(file_data, MAX_PDF_SIZE)
        try:
            validate_pdf(file_data)
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

    return inspection


def validate_pdf(
    file_data: bytes,
) -> None:
    if not file_data.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF file.")
    if b"%%EOF" not in file_data[-1024:]:
        raise ValueError("PDF appears to be incomplete.")
