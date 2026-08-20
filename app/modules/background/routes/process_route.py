"""Background removal start and replace endpoints."""

import logging

from fastapi import APIRouter, File, Form, UploadFile

from app.api import API_PREFIX
from app.modules.background.background_controller import (
    background_controller,
)
from app.modules.background.routes.background_route_helpers import (
    check_background_capability,
    record_job,
    validate_output_format,
)

logger = logging.getLogger(__name__)


def create_process_router() -> APIRouter:
    router = APIRouter(
        prefix=f"{API_PREFIX}/background",
        tags=["Background Removal"],
    )

    @router.post("/start")
    async def start_background(
        file: UploadFile = File(...),
        output_format: str = "webp",
    ):
        check_background_capability()
        logger.info(
            "Starting background removal for file: %s, format: %s",
            file.filename,
            output_format,
        )
        normalized_format = validate_output_format(output_format)
        result = await background_controller.remove_background(
            file,
            normalized_format,
        )
        job = record_job(result)
        logger.info(
            "Background removal completed for file: %s, job_id: %s",
            file.filename,
            job["job_id"],
        )
        return {
            "success": True,
            "job_id": job["job_id"],
            "status": "completed",
            "result": result,
        }

    @router.post("/replace")
    async def replace_background(
        file: UploadFile = File(...),
        color: str | None = Form(None),
        background_image: UploadFile | None = File(None),
        blur: int = Form(0),
        output_format: str = Form("png"),
    ):
        check_background_capability()
        logger.info(
            "Replacing background for file: %s",
            file.filename,
        )
        result = await background_controller.replace_background(
            file,
            color=color,
            background_image=background_image,
            blur=blur,
            output_format=output_format,
        )
        job = record_job(result)
        return {
            "success": True,
            "job_id": job["job_id"],
            "status": "completed",
            "result": result,
        }

    return router
