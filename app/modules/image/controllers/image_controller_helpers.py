"""Shared helpers for the image tool controllers."""

from fastapi import HTTPException, UploadFile

from app.modules.image.image_repository import image_repository
from app.modules.image.image_schema import ImageToolResult
from app.shared.file_inspection.file_validation import (
    inspect_and_validate,
)


async def read_image(file: UploadFile) -> tuple[bytes, str]:
    """Read and validate an uploaded image, returning (data, filename)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    file_data = await file.read()
    if not file_data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    inspection = inspect_and_validate(file_data)
    if inspection.category.value != "image":
        raise HTTPException(status_code=415, detail="Only image files are supported")
    return file_data, file.filename


def build_result(
    original_filename: str,
    result: dict,
    details: dict | None = None,
) -> ImageToolResult:
    """Persist processed bytes and build the standard tool result."""
    base_name = original_filename.rsplit(".", 1)[0]
    output_filename = f"{base_name}.{result['extension']}"
    output_path = image_repository.save_processed_file(
        result["data"],
        output_filename,
    )
    merged_details = {
        key: value
        for key, value in result.items()
        if key not in {"data", "content_type", "extension"}
    }
    if details:
        merged_details.update(details)
    return ImageToolResult(
        success=True,
        original_filename=original_filename,
        width=result.get("width", 0),
        height=result.get("height", 0),
        format=result["extension"],
        filename=output_path.name,
        size_bytes=len(result["data"]),
        download_url=f"/api/v1/tools/image/download/{output_path.name}",
        details=merged_details,
    )


def max_dimension_from_params(
    max_width: int | None,
    max_height: int | None,
) -> int | None:
    """Derive a single max_dimension value from max_width / max_height."""
    if max_width is not None and max_height is not None:
        return max(max_width, max_height)
    return max_width or max_height


def save_and_build_result(
    filename: str,
    result: dict,
    details: dict | None = None,
) -> tuple[str, dict]:
    """Persist result data and return (output_path_name, merged_details)."""
    base_name = filename.rsplit(".", 1)[0]
    output_filename = f"{base_name}.{result['extension']}"
    output_path = image_repository.save_processed_file(
        result["data"],
        output_filename,
    )
    merged = {
        key: value
        for key, value in result.items()
        if key not in {"data", "content_type", "extension"}
    }
    if details:
        merged.update(details)
    return output_path.name, merged


def resize_details(result: dict) -> dict:
    """Standard details block shared by single and batch resize results."""
    return {
        "input_format": result["input_format"],
        "original_width": result["original_width"],
        "original_height": result["original_height"],
        "original_size_bytes": result["original_size"],
        "output_format": result["extension"],
        "width": result["width"],
        "height": result["height"],
        "flattened": result.get("flattened", False),
        "has_alpha": result.get("has_alpha", False),
    }
