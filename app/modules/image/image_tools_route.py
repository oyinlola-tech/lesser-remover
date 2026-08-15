import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.api import API_PREFIX
from app.core.config import settings
from app.modules.image.image_repository import image_repository
from app.modules.image.image_schema import (
    ConvertBatchResult,
    ImageToolResult,
    ResizeBatchResult,
)
from app.modules.image.image_service import SUPPORTED_CONVERSION_FORMATS
from app.modules.image.image_tools_controller import (
    image_tools_controller,
)
from app.shared.utils.file_util import is_safe_filename

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{API_PREFIX}/tools/image",
    tags=["Image Tools"],
)

images_router = APIRouter(
    prefix=f"{API_PREFIX}/images",
    tags=["Image Tools"],
)


@router.post("/convert", response_model=ImageToolResult)
async def convert_image(
    file: UploadFile = File(...),
    output_format: str = Form("png"),
):
    logger.info("convert_image: file=%s format=%s", file.filename, output_format)
    return await image_tools_controller.convert(
        file,
        output_format,
    )


@images_router.post("/convert", response_model=ConvertBatchResult)
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

    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files were uploaded.",
        )

    if len(files) > 50:
        raise HTTPException(
            status_code=400,
            detail="Too many files. Maximum is 50.",
        )

    normalized = output_format.lower()
    if normalized not in SUPPORTED_CONVERSION_FORMATS:
        raise HTTPException(
            status_code=400,
            detail="Output format must be jpg, png, webp or avif.",
        )

    if quality is not None and (quality < 1 or quality > 100):
        raise HTTPException(
            status_code=400,
            detail="Quality must be between 1 and 100.",
        )

    if background_color is not None and not _is_valid_color(background_color):
        raise HTTPException(
            status_code=400,
            detail="Invalid background color.",
        )

    return await image_tools_controller.convert_batch(
        files,
        normalized,
        quality=quality,
        remove_metadata=remove_metadata,
        background_color=background_color,
        lossless=lossless,
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


@router.get("/social-presets")
async def social_presets():
    from app.shared.constants.social_presets import SOCIAL_PRESETS

    return {
        "success": True,
        "presets": SOCIAL_PRESETS,
    }


@router.get("/presets")
async def dimension_presets():
    from app.shared.constants.social_presets import STANDARD_PRESETS

    return {
        "success": True,
        "presets": STANDARD_PRESETS,
    }


@router.post("/crop", response_model=ImageToolResult)
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
        raise HTTPException(
            status_code=400,
            detail="Crop dimensions must be positive.",
        )
    if crop_x < 0 or crop_y < 0:
        raise HTTPException(
            status_code=400,
            detail="Crop coordinates must be non-negative.",
        )
    if rotation not in (0, 90, 180, 270):
        raise HTTPException(
            status_code=400,
            detail="Rotation must be 0, 90, 180 or 270 degrees.",
        )
    if quality is not None and (quality < 1 or quality > 100):
        raise HTTPException(
            status_code=400,
            detail="Quality must be between 1 and 100.",
        )
    if output_format.lower() != "auto" and output_format.lower() not in {"jpg", "jpeg", "png", "webp"}:
        raise HTTPException(
            status_code=400,
            detail="Output format must be auto, jpg, png or webp.",
        )
    if background_color is not None and not _is_valid_color(background_color):
        raise HTTPException(
            status_code=400,
            detail="Invalid background color.",
        )

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


@router.post("/remove-metadata", response_model=ImageToolResult)
async def remove_metadata(
    file: UploadFile = File(...),
):
    logger.info("remove_metadata: file=%s", file.filename)
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
    logger.info(
        "add_watermark: file=%s position=%s opacity=%s size_ratio=%s rotation=%s",
        file.filename, position, opacity, size_ratio, rotation,
    )
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


@images_router.post("/resize", response_model=ResizeBatchResult)
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

    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files were uploaded.",
        )

    if len(files) > 50:
        raise HTTPException(
            status_code=400,
            detail="Too many files. Maximum is 50.",
        )

    if resize_mode not in {"aspect", "exact", "percent", "max"}:
        raise HTTPException(
            status_code=400,
            detail="Resize mode must be aspect, exact, percent or max.",
        )

    if width is not None and width <= 0:
        raise HTTPException(
            status_code=400,
            detail="Width must be positive.",
        )
    if height is not None and height <= 0:
        raise HTTPException(
            status_code=400,
            detail="Height must be positive.",
        )
    if max_width is not None and max_width <= 0:
        raise HTTPException(
            status_code=400,
            detail="Maximum width must be positive.",
        )
    if max_height is not None and max_height <= 0:
        raise HTTPException(
            status_code=400,
            detail="Maximum height must be positive.",
        )

    if resize_mode == "percent" and (percent is None or percent <= 0):
        raise HTTPException(
            status_code=400,
            detail="Percentage must be greater than zero.",
        )

    if resize_mode in ("aspect", "exact") and width is None and height is None:
        raise HTTPException(
            status_code=400,
            detail="Provide width and/or height for this resize mode.",
        )

    if resize_mode == "max" and max_width is None and max_height is None:
        raise HTTPException(
            status_code=400,
            detail="Provide at least a maximum width or height.",
        )

    if quality is not None and (quality < 1 or quality > 100):
        raise HTTPException(
            status_code=400,
            detail="Quality must be between 1 and 100.",
        )

    if width is not None and width > settings.max_image_width:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Width exceeds the maximum of "
                f"{settings.max_image_width} pixels."
            ),
        )
    if height is not None and height > settings.max_image_height:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Height exceeds the maximum of "
                f"{settings.max_image_height} pixels."
            ),
        )
    if max_width is not None and max_width > settings.max_image_width:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Maximum width exceeds the maximum of "
                f"{settings.max_image_width} pixels."
            ),
        )
    if max_height is not None and max_height > settings.max_image_height:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Maximum height exceeds the maximum of "
                f"{settings.max_image_height} pixels."
            ),
        )

    if (
        output_format != "auto"
        and output_format.lower()
        not in {"jpg", "jpeg", "png", "webp"}
    ):
        raise HTTPException(
            status_code=400,
            detail="Output format must be auto, jpg, png, webp, or avif.",
        )

    if background_color is not None and not _is_valid_color(background_color):
        raise HTTPException(
            status_code=400,
            detail="Invalid background color.",
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


def _is_valid_color(value: str) -> bool:
    from app.infrastructure.compression.pillow_adapter import _parse_color
    try:
        _parse_color(value)
        return True
    except (ValueError, OSError):
        return False
