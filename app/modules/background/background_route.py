import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.modules.background.background_controller import (
    background_controller,
)
from app.modules.background.background_repository import (
    background_repository,
)
from app.shared.utils.file_util import is_safe_filename

router = APIRouter(
    prefix="/api/background",
    tags=["Background Removal"],
)

_background_jobs: dict[str, dict] = {}


def _validate_output_format(output_format: str) -> str:
    normalized = output_format.lower()
    if normalized not in {"webp", "png"}:
        raise HTTPException(
            status_code=400,
            detail="Output format must be WebP or PNG.",
        )
    return normalized


@router.post("/start")
async def start_background(
    file: UploadFile = File(...),
    output_format: str = "webp",
):
    normalized_format = _validate_output_format(output_format)
    result = await background_controller.remove_background(file, normalized_format)
    job_id = uuid.uuid4().hex
    _background_jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "result": result,
    }
    return {
        "success": True,
        "job_id": job_id,
        "status": "completed",
        "result": result,
    }


@router.get("/result/{job_id}")
async def get_background_result(job_id: str):
    job = _background_jobs.get(job_id)
    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Background job not found.",
        )
    return job


@router.get("/download/{filename}")
async def download_processed_file(
    filename: str,
):
    if not is_safe_filename(filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )
    file_path = (
        background_repository.get_processed_file(
            filename
        )
    )
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Processed file not found",
        )
    try:
        return FileResponse(
            path=file_path,
            media_type="image/png",
            filename=file_path.name,
        )
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="Processed file not found",
        ) from error