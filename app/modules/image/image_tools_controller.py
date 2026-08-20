from fastapi import HTTPException, UploadFile

from app.modules.image.image_repository import image_repository
from app.modules.image.image_schema import (
    ConvertBatchResult,
    ConvertResult,
    ImageToolResult,
    ResizeBatchResult,
    ResizeResult,
)
from app.modules.image.image_service import (
    SUPPORTED_CONVERSION_FORMATS,
    SUPPORTED_CROP_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    image_service,
)
from app.shared.file_inspection.file_validation import (
    inspect_and_validate,
)


def _max_dimension_from_params(
    max_width: int | None,
    max_height: int | None,
) -> int | None:
    """Derive a single max_dimension value from max_width / max_height."""
    if max_width is not None and max_height is not None:
        return max(max_width, max_height)
    return max_width or max_height


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
        quality: int | None = None,
        remove_metadata: bool = True,
        background_color: str | None = None,
        lossless: bool = False,
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
                quality=quality,
                strip_metadata=remove_metadata,
                background_color=background_color,
                lossless=lossless,
            )
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
            return self._result(filename, result, details)
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
                detail=(
                    "Output format must be jpg, png, webp or avif."
                ),
            )

        for file in files:
            try:
                file_data, filename = await self._read_image(file)

                result = image_service.convert(
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
                        "Transparent areas were filled."
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
                    details=details,
                ))
            except (HTTPException, ValueError, OSError, RuntimeError) as error:
                detail = (
                    error.detail
                    if hasattr(error, "detail")
                    else str(error)
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

        if percent is not None:
            resize_mode = "percent"
            resize_kwargs = {"percent": percent}
        elif width is not None and height is not None:
            resize_mode = "exact"
            resize_kwargs = {
                "width": width,
                "height": height,
                "maintain_aspect_ratio": False,
            }
        elif max_dimension is not None:
            resize_mode = "max"
            resize_kwargs = {"max_dimension": max_dimension}
        elif width is not None:
            resize_mode = "aspect"
            resize_kwargs = {"width": width}
        elif height is not None:
            resize_mode = "aspect"
            resize_kwargs = {"height": height}
        else:
            raise HTTPException(
                status_code=400,
                detail="Provide width, height, percentage or max dimension.",
            )

        try:
            result = image_service.resize(
                file_data,
                resize_mode=resize_mode,
                output_format=normalized,
                allow_upscale=cover,
                **resize_kwargs,
            )
            return self._result(filename, result)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to resize image: {error}",
            ) from error

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
        file_data, filename = await self._read_image(file)

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
            result = image_service.crop(
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
            return self._result(filename, result, details)
        except (OSError, ValueError, RuntimeError) as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to crop image: {error}",
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
        file_data, filename = await self._read_image(file)

        if output_format == "auto":
            pass
        else:
            normalized = output_format.lower()
            if normalized not in SUPPORTED_OUTPUT_FORMATS:
                raise HTTPException(
                    status_code=400,
                    detail="Output format must be auto, jpg, png, webp or avif.",
                )

        if resize_mode == "max":
            max_dimension = _max_dimension_from_params(
                max_width, max_height
            )
        else:
            max_dimension = None

        try:
            result = image_service.resize(
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
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

        base_name = filename.rsplit(".", 1)[0]
        output_filename = f"{base_name}.{result['extension']}"
        output_path = image_repository.save_processed_file(
            result["data"],
            output_filename,
        )

        details = {
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
            details=details,
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
                file_data, filename = await self._read_image(file)

                if output_format != "auto":
                    normalized = output_format.lower()
                    if normalized not in SUPPORTED_OUTPUT_FORMATS:
                        raise ValueError(
                            "Output format must be auto, jpg, png, or webp."
                        )

                if resize_mode == "max":
                    max_dimension = _max_dimension_from_params(
                        max_width, max_height
                    )
                else:
                    max_dimension = None

                result = image_service.resize(
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

                details = {
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
                    details=details,
                ))
            except (HTTPException, ValueError) as error:
                detail = (
                    error.detail
                    if hasattr(error, "detail")
                    else str(error)
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

    async def extract_palette(
        self,
        file: UploadFile,
        num_colors: int = 6,
    ) -> dict:
        file_data, filename = await self._read_image(file)
        try:
            colors = image_service.extract_palette(file_data, num_colors=num_colors)
            return {"success": True, "filename": filename, "colors": colors}
        except ValueError as err:
            raise HTTPException(status_code=400, detail=str(err))


image_tools_controller = ImageToolsController()
