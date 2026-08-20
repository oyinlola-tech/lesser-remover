"""HTTP-facing logic for the image-resizer tool."""

from fastapi import HTTPException, UploadFile

from app.modules.image.controllers.image_controller_helpers import (
    build_result,
    max_dimension_from_params,
    read_image,
)
from app.modules.image.image_repository import image_repository
from app.modules.image.image_schema import (
    ImageToolResult,
    ResizeBatchResult,
    ResizeResult,
)
from app.modules.image.services.image_helpers import (
    SUPPORTED_CONVERSION_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
)
from app.modules.image.services.resizer_service import image_resizer_service


class ResizeController:
    """Resize single or batched images with full options."""

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
        file_data, filename = await read_image(file)
        normalized = output_format.lower()
        if normalized not in SUPPORTED_CONVERSION_FORMATS:
            raise HTTPException(
                status_code=400,
                detail="Output format must be jpg, png, webp or avif.",
            )

        resize_mode, resize_kwargs = self._infer_mode(
            width, height, percent, max_dimension
        )

        try:
            result = image_resizer_service.resize(
                file_data,
                resize_mode=resize_mode,
                output_format=normalized,
                allow_upscale=cover,
                **resize_kwargs,
            )
            return build_result(filename, result)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to resize image: {error}",
            ) from error

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
        """Resize a single image with full options.

        Uses the shared storage abstraction so the result is portable
        between local and future Vercel runtimes.
        """
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

        try:
            result = image_resizer_service.resize(
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
            details=self._details(result),
        )

    async def resize_batch(
        self,
        files: list[UploadFile],
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
    ) -> ResizeBatchResult:
        """Resize multiple images with the same configuration.

        Processes valid files and reports failures individually.
        Per-file validation failures (corrupt images, non-image files)
        are collected as failures rather than aborting the entire batch.
        """
        results: list[ResizeResult] = []
        failures: list[dict] = []

        for file in files:
            try:
                file_data, filename = await read_image(file)

                if output_format != "auto":
                    normalized = output_format.lower()
                    if normalized not in SUPPORTED_OUTPUT_FORMATS:
                        raise ValueError(
                            "Output format must be auto, jpg, png, or webp."
                        )

                if resize_mode == "max":
                    max_dimension = max_dimension_from_params(
                        max_width, max_height
                    )
                else:
                    max_dimension = None

                result = image_resizer_service.resize(
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

                base_name = filename.rsplit(".", 1)[0]
                output_filename = f"{base_name}.{result['extension']}"
                output_path = image_repository.save_processed_file(
                    result["data"],
                    output_filename,
                )

                results.append(ResizeResult(
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
                    details=self._details(result),
                ))
            except (HTTPException, ValueError) as error:
                detail = (
                    error.detail if hasattr(error, "detail") else str(error)
                )
                failures.append({
                    "filename": file.filename or "unknown",
                    "error": detail,
                })
            except (OSError, RuntimeError) as error:
                failures.append({
                    "filename": file.filename or "unknown",
                    "error": f"Unable to process image: {error}",
                })

        return ResizeBatchResult(
            success=True,
            total_files=len(files),
            successful_files=len(results),
            failed_files=len(failures),
            results=results,
            failures=failures,
        )

    @staticmethod
    def _infer_mode(
        width: int | None,
        height: int | None,
        percent: float | None,
        max_dimension: int | None,
    ) -> tuple[str, dict]:
        if percent is not None:
            return "percent", {"percent": percent}
        if width is not None and height is not None:
            return "exact", {
                "width": width,
                "height": height,
                "maintain_aspect_ratio": False,
            }
        if max_dimension is not None:
            return "max", {"max_dimension": max_dimension}
        if width is not None:
            return "aspect", {"width": width}
        if height is not None:
            return "aspect", {"height": height}
        raise HTTPException(
            status_code=400,
            detail="Provide width, height, percentage or max dimension.",
        )

    @staticmethod
    def _details(result: dict) -> dict:
        return {
            "input_format": result["input_format"],
            "original_width": result["original_width"],
            "original_height": result["original_height"],
            "original_size_bytes": result["original_size"],
            "output_format": result["extension"],
            "width": result["width"],
            "height": result["height"],
            "flattened": result.get("flattened", False),
            "has_alpha": result.get("has_alpha", False),
        }


resize_controller = ResizeController()
