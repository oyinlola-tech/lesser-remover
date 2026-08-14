import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.api import API_PREFIX
from app.modules.image.image_repository import image_repository
from app.modules.image.image_schema import (
    ImageToolListResult,
    ImageToolResult,
)
from app.modules.image.image_tools_controller import (
    image_tools_controller,
)
from app.shared.utils.file_util import is_safe_filename

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{API_PREFIX}/tools/image",
    tags=["Image Tools"],
)


@router.post("/convert", response_model=ImageToolResult)
async def convert_image(
    file: UploadFile = File(...),
    output_format: str = Form("png"),
):
    return await image_tools_controller.convert(
        file,
        output_format,
    )


@router.post("/resize", response_model=ImageToolResult)
async def resize_image(
    file: UploadFile = File(...),
    width: int | None = Form(None),
    height: int | None = Form(None),
    percent: float | None = Form(None),
    max_dimension: int | None = Form(None),
    output_format: str = Form("png"),
    cover: bool = Form(False),
):
    return await image_tools_controller.resize(
        file,
        width=width,
        height=height,
        percent=percent,
        max_dimension=max_dimension,
        output_format=output_format,
        cover=cover,
    )


@router.get("/social-presets")
async def social_presets():
    from app.shared.constants.social_presets import SOCIAL_PRESETS

    return {
        "success": True,
        "presets": SOCIAL_PRESETS,
    }


@router.post("/remove-metadata", response_model=ImageToolResult)
async def remove_metadata(
    file: UploadFile = File(...),
):
    return await image_tools_controller.remove_metadata(file)


@router.post("/watermark", response_model=ImageToolResult)
async def add_watermark(
    file: UploadFile = File(...),
    text: str | None = Form(None),
    logo: UploadFile | None = File(None),
    position: str = Form("bottom-right"),
    opacity: float = Form(0.7),
    size_ratio: float = Form(0.1),
    rotation: int = Form(0),
):
    return await image_tools_controller.add_watermark(
        file,
        text=text,
        logo=logo,
        position=position,
        opacity=opacity,
        size_ratio=size_ratio,
        rotation=rotation,
    )


@router.get("/download/{filename}")
async def download_processed_file(
    filename: str,
):
    if not is_safe_filename(filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )
    file_path = image_repository.get_processed_file(filename)
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Processed file not found",
        )
    content_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".avif": "image/avif",
    }
    media_type = content_types.get(
        file_path.suffix.lower(),
        "application/octet-stream",
    )
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=file_path.name,
    )
