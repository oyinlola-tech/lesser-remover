"""HTTP-facing logic for the image-converter tool."""

from fastapi import HTTPException, UploadFile

from app.modules.image.controllers.image_controller_helpers import (
    build_result,
    read_image,
)
from app.modules.image.image_repository import image_repository
from app.modules.image.image_schema import ConvertBatchResult, ConvertResult
from app.modules.image.services.converter_service import image_converter_service
from app.modules.image.services.image_helpers import SUPPORTED_CONVERSION_FORMATS


class ConvertController:
    """Convert single or batched images between formats."""

    async def convert(
        self,
        file: UploadFile,
        output_format: str,
        quality: int | None = None,
        remove_metadata: bool = True,
        background_color: str | None = None,
        lossless: bool = False,
    ) -> object:
        file_data, filename = await read_image(file)
        normalized = output_format.lower()
        if normalized not in SUPPORTED_CONVERSION_FORMATS:
            raise HTTPException(
                status_code=400,
                detail="Output format must be jpg, png, webp or avif.",
            )
        try:
            result = image_converter_service.convert(
                file_data,
                normalized,
                quality=quality,
                strip_metadata=remove_metadata,
                background_color=background_color,
                lossless=lossless,
            )
            details = self._details(result)
            return build_result(filename, result, details)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to convert image: {error}",
            ) from error

    async def convert_batch(
        self,
        files: list[UploadFile],
        output_format: str,
        quality: int | None = None,
        remove_metadata: bool = True,
        background_color: str | None = None,
        lossless: bool = False,
    ) -> ConvertBatchResult:
        """Convert multiple images with the same configuration.

        Processes valid files and reports failures individually.
        """
        results: list[ConvertResult] = []
        failures: list[dict] = []

        normalized = output_format.lower()
        if normalized not in SUPPORTED_CONVERSION_FORMATS:
            raise HTTPException(
                status_code=400,
                detail="Output format must be jpg, png, webp or avif.",
            )

        for file in files:
            try:
                file_data, filename = await read_image(file)

                result = image_converter_service.convert(
                    file_data,
                    normalized,
                    quality=quality,
                    strip_metadata=remove_metadata,
                    background_color=background_color,
                    lossless=lossless,
                )

                base_name = filename.rsplit(".", 1)[0]
                output_filename = f"{base_name}.{result['extension']}"
                output_path = image_repository.save_processed_file(
                    result["data"],
                    output_filename,
                )

                results.append(ConvertResult(
                    success=True,
                    original_filename=filename,
                    output_filename=output_path.name,
                    input_format=result.get("input_format", ""),
                    output_format=result["extension"],
                    original_width=result.get("original_width", 0),
                    original_height=result.get("original_height", 0),
                    width=result["width"],
                    height=result["height"],
                    original_size_bytes=result.get("original_size", 0),
                    size_bytes=len(result["data"]),
                    download_url=f"/api/v1/tools/image/download/{output_path.name}",
                    details=self._details(result),
                ))
            except (HTTPException, ValueError, OSError, RuntimeError) as error:
                detail = (
                    error.detail if hasattr(error, "detail") else str(error)
                )
                failures.append({
                    "filename": file.filename or "unknown",
                    "error": detail,
                })

        return ConvertBatchResult(
            success=True,
            total_files=len(files),
            successful_files=len(results),
            failed_files=len(failures),
            results=results,
            failures=failures,
        )

    @staticmethod
    def _details(result: dict) -> dict:
        details = {
            "input_format": result.get("input_format", ""),
            "original_width": result.get("original_width", 0),
            "original_height": result.get("original_height", 0),
            "original_size_bytes": result.get("original_size", 0),
            "flattened": result.get("flattened", False),
            "has_alpha": result.get("has_alpha", False),
        }
        if details["flattened"]:
            details["transparency_info"] = (
                "JPEG cannot preserve transparency. "
                "Transparent areas were filled with the background color."
            )
        return details


convert_controller = ConvertController()
