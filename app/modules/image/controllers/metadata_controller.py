"""HTTP-facing logic for the metadata-remover tool."""

from fastapi import HTTPException, UploadFile

from app.modules.image.controllers.image_controller_helpers import (
    build_result,
    read_image,
)
from app.modules.image.image_schema import ImageToolResult
from app.modules.image.services.metadata_remover_service import (
    metadata_remover_service,
)


class MetadataController:
    """Strip EXIF/GPS/camera metadata from an image."""

    async def remove_metadata(self, file: UploadFile) -> ImageToolResult:
        file_data, filename = await read_image(file)
        try:
            result = metadata_remover_service.remove_metadata(file_data)
            details = {
                "removed_metadata": result.get("removed_metadata", [])
            }
            return build_result(filename, result, details)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to remove metadata: {error}",
            ) from error


metadata_controller = MetadataController()
