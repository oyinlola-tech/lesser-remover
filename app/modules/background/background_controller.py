from fastapi import HTTPException, UploadFile
from app.modules.background.background_schema import (
    BackgroundRemovalResponse,
)
from app.modules.background.background_service import (
    background_service,
)
from app.modules.background.background_repository import (
    background_repository,
)
from app.modules.image.image_service import image_service
from app.modules.image.image_schema import ImageVariant
from app.shared.file_inspection.file_validation import (
    inspect_and_validate,
)


class BackgroundController:
    async def remove_background(
        self,
        file: UploadFile,
        output_format: str = "webp",
    ) -> BackgroundRemovalResponse:
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
        try:
            (
                processed_image,
                width,
                height,
            ) = background_service.remove_background(
                file_data=file_data,
                original_filename=file.filename,
            )

            from io import BytesIO

            output_buffer = BytesIO()
            if output_format == "png":
                processed_image.save(output_buffer, format="PNG")
                extension = ".png"
            else:
                processed_image.save(
                    output_buffer,
                    format="WEBP",
                    quality=95,
                    method=6,
                )
                extension = ".webp"

            final_data = output_buffer.getvalue()
            output_filename = file.filename.rsplit(".", 1)[0] + extension
            output_path = background_repository.save_processed_file(
                final_data,
                output_filename,
            )

            return {
                "success": True,
                "original_filename": file.filename,
                "width": width,
                "height": height,
                "format": output_format,
                "filename": output_path.name,
                "size_bytes": len(final_data),
                "download_url": f"/api/background/download/{output_path.name}",
            }
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to process image: {error}",
            ) from error


background_controller = BackgroundController()
