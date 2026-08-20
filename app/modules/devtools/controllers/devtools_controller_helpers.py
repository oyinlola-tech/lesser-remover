"""Shared helpers for the devtools controllers."""

from fastapi import HTTPException, UploadFile


async def read_upload(
    file: UploadFile | None,
    field: str,
) -> bytes | None:
    """Read an optional upload, raising 400 for empty files."""
    if file is None:
        return None
    file_data = await file.read()
    if not file_data:
        raise HTTPException(
            status_code=400,
            detail=f"Uploaded file is empty: {field}",
        )
    return file_data


def as_http_error(prefix: str, error: Exception) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=f"{prefix}: {error}",
    )
