from fastapi import HTTPException, UploadFile

from app.modules.image.image_repository import image_repository
from app.modules.image.image_schema import ImageToolResult
from app.modules.image.image_service import (
    SUPPORTED_CONVERSION_FORMATS,
    image_service,
)
from app.shared.file_inspection.file_validation import (
    inspect_and_validate,
)


def _content_type_for(extension: str) -> str:
    return {
        "jpg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "avif": "image/avif",
        "zip": "application/zip",
    }.get(extension, "application/octet-stream")


class ImageToolsController:
    async def _read_image(
        self,
        file: UploadFile,
    ) -> tuple[bytes, str]:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required",
            )
        file_data = await file.read()
        if not file_data:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty",
            )
        inspection = inspect_and_validate(file_data)
        if inspection.category.value != "image":
            raise HTTPException(
                status_code=415,
                detail="Only image files are supported",
            )
        return file_data, file.filename

    def _result(
        self,
        original_filename: str,
        result: dict,
        details: dict | None = None,
    ) -> ImageToolResult:
        base_name = original_filename.rsplit(".", 1)[0]
        output_filename = f"{base_name}.{result['extension']}"
        output_path = image_repository.save_processed_file(
            result["data"],
            output_filename,
        )
        merged_details = {
            key: value
            for key, value in result.items()
            if key not in {
                "data",
                "content_type",
                "extension",
            }
        }
        if details:
            merged_details.update(details)
        return ImageToolResult(
            success=True,
            original_filename=original_filename,
            width=result.get("width", 0),
            height=result.get("height", 0),
            format=result["extension"],
            filename=output_path.name,
            size_bytes=len(result["data"]),
            download_url=f"/api/v1/tools/image/download/{output_path.name}",
            details=merged_details,
        )

    async def convert(
        self,
        file: UploadFile,
        output_format: str,
    ) -> ImageToolResult:
        file_data, filename = await self._read_image(file)
        normalized = output_format.lower()
        if normalized not in SUPPORTED_CONVERSION_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Output format must be jpg, png, webp or avif."
                ),
            )
        try:
            result = image_service.convert(
                file_data,
                normalized,
            )
            return self._result(filename, result)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to convert image: {error}",
            ) from error

    async def resize(
        self,
        file: UploadFile,
        width: int | None = None,
        height: int | None = None,
        percent: float | None = None,
        max_dimension: int | None = None,
        output_format: str = "png",
        cover: bool = False,
    ) -> ImageToolResult:
        file_data, filename = await self._read_image(file)
        normalized = output_format.lower()
        if normalized not in SUPPORTED_CONVERSION_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Output format must be jpg, png, webp or avif."
                ),
            )
        try:
            result = image_service.resize(
                file_data,
                width=width,
                height=height,
                percent=percent,
                max_dimension=max_dimension,
                output_format=normalized,
                cover=cover,
            )
            return self._result(filename, result)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to resize image: {error}",
            ) from error

    async def remove_metadata(
        self,
        file: UploadFile,
    ) -> ImageToolResult:
        file_data, filename = await self._read_image(file)
        try:
            result = image_service.remove_metadata(file_data)
            details = {
                "removed_metadata": result.get(
                    "removed_metadata",
                    [],
                )
            }
            return self._result(filename, result, details)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to remove metadata: {error}",
            ) from error

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
        file_data, filename = await self._read_image(file)
        logo_data = None
        if logo is not None:
            logo_data = await logo.read()
        if not text and not logo_data:
            raise HTTPException(
                status_code=400,
                detail="Provide watermark text or a logo image.",
            )
        try:
            result = image_service.add_watermark(
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
            return self._result(filename, result, details)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to add watermark: {error}",
            ) from error


image_tools_controller = ImageToolsController()
