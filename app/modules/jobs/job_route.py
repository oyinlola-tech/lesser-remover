import logging

from fastapi import APIRouter, HTTPException

from app.api import API_PREFIX
from app.modules.jobs.job_controller import (
    job_controller,
)
from app.modules.jobs.job_service import (
    job_service,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{API_PREFIX}/jobs",
    tags=["Jobs"],
)


@router.get("/{job_id}")
async def get_job(
    job_id: str,
):
    logger.debug("Job status requested: %s", job_id)
    return job_controller.get_job(job_id)


@router.delete("/{job_id}")
async def cancel_job(
    job_id: str,
):
    logger.info("Job cancellation requested: %s", job_id)
    job = job_service.get(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )
    job_service.cancel(job_id)
    return {
        "success": True,
        "job_id": job_id,
        "status": "cancelled",
    }
