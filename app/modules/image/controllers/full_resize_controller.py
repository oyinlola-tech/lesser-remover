"""Full-options single resize logic for the image-resizer tool."""

from fastapi import HTTPException, UploadFile

from app.modules.image.controllers.image_controller_helpers import (
    max_dimension_from_params,
    read_image,
    resize_details,
)
from app.modules.image.image_repository import image_repository
from app.modules.image.image_schema import ResizeResult
from app.modules.image.services.image_helpers import SUPPORTED_OUTPUT_FORMATS
from app.modules.image.services.resizer_service import image_resizer_service


class FullResizeController:
    """Resize a single image with full options."""

    async def resize_image(
        self,
        file: UploadFile,
        resize_mode: str = "aspect",
        width: int | None = None,
        height: int | None = None,
        percent: float | None = None,
        max_width: int | None = None,
        max_height: int | None = None,
        maintain_aspect_ratio: bool = True,
        allow_upscale: bool = False,
        output_format: str = "auto",
        quality: int | None = None,
        remove_metadata: bool = True,
        background_color: str | None = None,
    ) -> ResizeResult:
        """Resize a single image with full options."""
        file_data, filename = await read_image(file)

        if output_format != "auto":
            normalized = output_format.lower()
            if normalized not in SUPPORTED_OUTPUT_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail="Output format must be auto, jpg, png, webp or avif.",
                )

        if resize_mode == "max":
            max_dimension = max_dimension_from_params(max_width, max_height)
        else:
            max_dimension = None

        result = self._run_resize(
            file_data, resize_mode, width, height, percent,
            max_dimension, maintain_aspect_ratio, allow_upscale,
            output_format, quality, remove_metadata, background_color,
        )

        base_name = filename.rsplit(".", 1)[0]
        output_filename = f"{base_name}.{result['extension']}"
        output_path = image_repository.save_processed_file(
            result["data"],
            output_filename,
        )

        return ResizeResult(
            success=True,
            original_filename=filename,
            output_filename=output_path.name,
            input_format=result["input_format"],
            output_format=result["extension"],
            original_width=result["original_width"],
            original_height=result["original_height"],
            width=result["width"],
            height=result["height"],
            original_size_bytes=result["original_size"],
            size_bytes=len(result["data"]),
            download_url=f"/api/v1/tools/image/download/{output_path.name}",
            details=resize_details(result),
        )

    @staticmethod
    def _run_resize(
        file_data: bytes,
        resize_mode: str,
        width: int | None,
        height: int | None,
        percent: float | None,
        max_dimension: int | None,
        maintain_aspect_ratio: bool,
        allow_upscale: bool,
        output_format: str,
        quality: int | None,
        remove_metadata: bool,
        background_color: str | None,
    ) -> dict:
        try:
            return image_resizer_service.resize(
                file_data,
                resize_mode=resize_mode,
                width=width,
                height=height,
                percent=percent,
                max_dimension=max_dimension,
                maintain_aspect_ratio=maintain_aspect_ratio,
                allow_upscale=allow_upscale,
                output_format=output_format,
                quality=quality,
                strip_metadata=remove_metadata,
                background_color=background_color,
            )
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(status_code=400, detail=str(error)) from error


full_resize_controller = FullResizeController()
