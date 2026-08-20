"""Routes for the image-converter tool."""

import logging

from fastapi import APIRouter, File, Form, UploadFile

from app.modules.image.image_schema import ConvertBatchResult, ImageToolResult
from app.modules.image.image_tools_controller import image_tools_controller
from app.modules.image.routes.route_helpers import (
    validate_background_color,
    validate_batch_files,
    validate_conversion_format,
    validate_quality,
)

logger = logging.getLogger(__name__)

convert_router = APIRouter(tags=["Image Tools"])
convert_batch_router = APIRouter(tags=["Image Tools"])


@convert_router.post("/convert", response_model=ImageToolResult)
async def convert_image(
    file: UploadFile = File(...),
    output_format: str = Form("png"),
):
    logger.info("convert_image: file=%s format=%s", file.filename, output_format)
    return await image_tools_controller.convert(file, output_format)


@convert_batch_router.post("/convert", response_model=ConvertBatchResult)
async def convert_images(
    files: list[UploadFile] = File(...),
    output_format: str = Form("png"),
    quality: int | None = Form(None),
    remove_metadata: bool = Form(True),
    background_color: str | None = Form(None),
    lossless: bool = Form(False),
):
    logger.info(
        "convert_images: files=%d format=%s quality=%s strip=%s bg=%s lossless=%s",
        len(files), output_format, quality, remove_metadata,
        background_color, lossless,
    )

    validate_batch_files(files)
    validate_conversion_format(output_format)
    validate_quality(quality)
    validate_background_color(background_color)

    return await image_tools_controller.convert_batch(
        files,
        output_format.lower(),
        quality=quality,
        remove_metadata=remove_metadata,
        background_color=background_color,
        lossless=lossless,
    )
