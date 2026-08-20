"""Routes for the image-cropper tool."""

import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.modules.image.image_schema import ImageToolResult
from app.modules.image.image_tools_controller import image_tools_controller
from app.modules.image.routes.route_helpers import (
    validate_background_color,
    validate_quality,
)

logger = logging.getLogger(__name__)

crop_router = APIRouter(tags=["Image Tools"])


@crop_router.post("/crop", response_model=ImageToolResult)
async def crop_image(
    file: UploadFile = File(...),
    crop_x: int = Form(0),
    crop_y: int = Form(0),
    crop_width: int = Form(...),
    crop_height: int = Form(...),
    rotation: int = Form(0),
    flip_horizontal: bool = Form(False),
    flip_vertical: bool = Form(False),
    output_format: str = Form("auto"),
    quality: int | None = Form(None),
    remove_metadata: bool = Form(True),
    background_color: str | None = Form(None),
):
    logger.info(
        "crop_image: file=%s x=%d y=%d w=%d h=%d rot=%d flip_h=%s flip_v=%s",
        file.filename, crop_x, crop_y, crop_width, crop_height,
        rotation, flip_horizontal, flip_vertical,
    )

    if crop_width <= 0 or crop_height <= 0:
        raise HTTPException(status_code=400, detail="Crop dimensions must be positive.")
    if crop_x < 0 or crop_y < 0:
        raise HTTPException(status_code=400, detail="Crop coordinates must be non-negative.")
    if rotation not in (0, 90, 180, 270):
        raise HTTPException(
            status_code=400,
            detail="Rotation must be 0, 90, 180 or 270 degrees.",
        )
    validate_quality(quality)
    if output_format.lower() not in {"auto", "jpg", "jpeg", "png", "webp"}:
        raise HTTPException(
            status_code=400,
            detail="Output format must be auto, jpg, png or webp.",
        )
    validate_background_color(background_color)

    return await image_tools_controller.crop(
        file,
        crop_x=crop_x,
        crop_y=crop_y,
        crop_width=crop_width,
        crop_height=crop_height,
        rotation=rotation,
        flip_horizontal=flip_horizontal,
        flip_vertical=flip_vertical,
        output_format=output_format,
        quality=quality,
        remove_metadata=remove_metadata,
        background_color=background_color,
    )
