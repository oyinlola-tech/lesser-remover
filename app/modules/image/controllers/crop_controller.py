"""HTTP-facing logic for the image-cropper tool."""

from fastapi import HTTPException, UploadFile

from app.modules.image.controllers.image_controller_helpers import (
    build_result,
    read_image,
)
from app.modules.image.image_schema import ImageToolResult
from app.modules.image.services.cropper_service import image_cropper_service
from app.modules.image.services.image_helpers import SUPPORTED_CROP_FORMATS


class CropController:
    """Crop an image with optional rotation and flip."""

    async def crop(
        self,
        file: UploadFile,
        crop_x: int = 0,
        crop_y: int = 0,
        crop_width: int | None = None,
        crop_height: int | None = None,
        rotation: int = 0,
        flip_horizontal: bool = False,
        flip_vertical: bool = False,
        output_format: str = "auto",
        quality: int | None = None,
        remove_metadata: bool = True,
        background_color: str | None = None,
    ) -> ImageToolResult:
        file_data, filename = await read_image(file)

        if crop_width is None or crop_height is None:
            raise HTTPException(
                status_code=400,
                detail="crop_width and crop_height are required.",
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

        normalized = output_format.lower()
        if normalized not in SUPPORTED_CROP_FORMATS:
            raise HTTPException(
                status_code=400,
                detail="Output format must be auto, jpg, png or webp.",
            )

        try:
            result = image_cropper_service.crop(
                file_data,
                crop_x=crop_x,
                crop_y=crop_y,
                crop_width=crop_width,
                crop_height=crop_height,
                rotation=rotation,
                flip_horizontal=flip_horizontal,
                flip_vertical=flip_vertical,
                output_format=normalized,
                quality=quality,
                strip_metadata=remove_metadata,
                background_color=background_color,
            )
            details = {
                "input_format": result.get("input_format", ""),
                "original_width": result.get("original_width", 0),
                "original_height": result.get("original_height", 0),
                "original_size_bytes": result.get("original_size", 0),
                "rotation": rotation,
                "flip_horizontal": flip_horizontal,
                "flip_vertical": flip_vertical,
                "flattened": result.get("flattened", False),
                "has_alpha": result.get("has_alpha", False),
            }
            if details["flattened"]:
                details["transparency_info"] = (
                    "JPEG cannot preserve transparency. "
                    "Transparent areas were filled."
                )
            return build_result(filename, result, details)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to crop image: {error}",
            ) from error


crop_controller = CropController()
