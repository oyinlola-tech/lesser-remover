"""Routes for the image-resizer tool."""

import logging

from fastapi import APIRouter, File, Form, UploadFile

from app.modules.image.image_schema import ImageToolResult, ResizeBatchResult
from app.modules.image.image_tools_controller import image_tools_controller
from app.modules.image.routes.route_helpers import (
    validate_batch_files,
    validate_resize_params,
)

logger = logging.getLogger(__name__)

resize_router = APIRouter(tags=["Image Tools"])
resize_batch_router = APIRouter(tags=["Image Tools"])


@resize_router.post("/resize", response_model=ImageToolResult)
async def resize_image(
    file: UploadFile = File(...),
    width: int | None = Form(None),
    height: int | None = Form(None),
    percent: float | None = Form(None),
    max_dimension: int | None = Form(None),
    output_format: str = Form("png"),
    cover: bool = Form(False),
):
    logger.info(
        "resize_image: file=%s w=%s h=%s pct=%s max=%s fmt=%s cover=%s",
        file.filename, width, height, percent,
        max_dimension, output_format, cover,
    )
    return await image_tools_controller.resize(
        file,
        width=width,
        height=height,
        percent=percent,
        max_dimension=max_dimension,
        output_format=output_format,
        cover=cover,
    )


@resize_batch_router.post("/resize", response_model=ResizeBatchResult)
async def resize_images(
    files: list[UploadFile] = File(...),
    resize_mode: str = Form("aspect"),
    width: int | None = Form(None),
    height: int | None = Form(None),
    percent: float | None = Form(None),
    max_width: int | None = Form(None),
    max_height: int | None = Form(None),
    maintain_aspect_ratio: bool = Form(True),
    allow_upscale: bool = Form(False),
    output_format: str = Form("auto"),
    quality: int | None = Form(None),
    remove_metadata: bool = Form(True),
    background_color: str | None = Form(None),
):
    logger.info(
        "resize_images: files=%d mode=%s width=%s height=%s percent=%s "
        "max_w=%s max_h=%s maintain_ar=%s upscale=%s format=%s quality=%s",
        len(files), resize_mode, width, height, percent,
        max_width, max_height, maintain_aspect_ratio,
        allow_upscale, output_format, quality,
    )

    validate_batch_files(files)
    validate_resize_params(
        resize_mode,
        width,
        height,
        percent,
        max_width,
        max_height,
        quality,
        output_format,
        background_color,
    )

    return await image_tools_controller.resize_batch(
        files,
        resize_mode=resize_mode,
        width=width,
        height=height,
        percent=percent,
        max_width=max_width,
        max_height=max_height,
        maintain_aspect_ratio=maintain_aspect_ratio,
        allow_upscale=allow_upscale,
        output_format=output_format,
        quality=quality,
        remove_metadata=remove_metadata,
        background_color=background_color,
    )
