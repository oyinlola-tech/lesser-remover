"""HTTP-facing logic for the watermark tool."""

from fastapi import HTTPException, UploadFile

from app.modules.image.controllers.image_controller_helpers import (
    build_result,
    read_image,
)
from app.modules.image.image_schema import ImageToolResult
from app.modules.image.services.watermark_service import watermark_service


class WatermarkController:
    """Overlay a text or logo watermark onto an image."""

    async def add_watermark(
        self,
        file: UploadFile,
        text: str | None = None,
        logo: UploadFile | None = None,
        position: str = "bottom-right",
        opacity: float = 0.7,
        size_ratio: float = 0.1,
        rotation: int = 0,
    ) -> ImageToolResult:
        file_data, filename = await read_image(file)
        logo_data = None
        if logo is not None:
            logo_data = await logo.read()
        if not text and not logo_data:
            raise HTTPException(
                status_code=400,
                detail="Provide watermark text or a logo image.",
            )
        try:
            result = watermark_service.add_watermark(
                file_data,
                text=text,
                logo_data=logo_data,
                position=position,
                opacity=opacity,
                size_ratio=size_ratio,
                rotation=rotation,
            )
            details = {
                "position": position,
                "opacity": opacity,
                "rotation": rotation,
            }
            return build_result(filename, result, details)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to add watermark: {error}",
            ) from error


watermark_controller = WatermarkController()
