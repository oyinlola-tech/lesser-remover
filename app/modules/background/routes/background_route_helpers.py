"""Background route helpers."""

import logging
import uuid

from fastapi import HTTPException

from app.core.capabilities import capability_registry

logger = logging.getLogger(__name__)

background_jobs: dict[str, dict] = {}


def check_background_capability() -> None:
    if not capability_registry.is_available("background-remover"):
        raise HTTPException(
            status_code=503,
            detail="Background removal is unavailable in the current environment.",
        )


def validate_output_format(output_format: str) -> str:
    normalized = output_format.lower()
    if normalized not in {"webp", "png"}:
        raise HTTPException(
            status_code=400,
            detail="Output format must be WebP or PNG.",
        )
    return normalized


def record_job(result: dict) -> dict:
    job_id = uuid.uuid4().hex
    background_jobs[job_id] = {
        "job_id": job_id,
        "status": "completed",
        "result": result,
    }
    return background_jobs[job_id]
