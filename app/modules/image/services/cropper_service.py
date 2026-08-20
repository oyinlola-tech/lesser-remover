"""Image cropping logic for the image-cropper tool."""

import time

from PIL import Image

from app.core.logging import get_tool_logger
from app.infrastructure.compression.pillow_adapter import pillow_adapter
from app.modules.image.services.image_helpers import (
    SUPPORTED_OUTPUT_FORMATS,
    has_transparency,
    is_animated,
    open_image,
    prepare_for_output,
)


class ImageCropperService:
    """Crop images with optional rotation and flip."""

    def crop(
        self,
        file_data: bytes,
        crop_x: int,
        crop_y: int,
        crop_width: int,
        crop_height: int,
        rotation: int = 0,
        flip_horizontal: bool = False,
        flip_vertical: bool = False,
        output_format: str = "auto",
        quality: int | None = None,
        strip_metadata: bool = True,
        background_color: str | None = None,
    ) -> dict:
        """Crop an image with optional rotation and flip.

        Transformation order:
            load -> rotate -> flip -> crop -> encode

        All pixel coordinates (``crop_x``, ``crop_y``, ``crop_width``,
        ``crop_height``) refer to the *original* image orientation (before
        rotation or flip).
        """
        tool_logger = get_tool_logger("image-cropper")
        started = time.monotonic()
        image = open_image(file_data)

        if is_animated(image):
            raise ValueError("Animated images are not supported for cropping.")

        input_format = (image.format or "unknown").upper()
        original_size = len(file_data)
        original_width = image.width
        original_height = image.height

        if rotation not in (0, 90, 180, 270):
            raise ValueError("Rotation must be 0, 90, 180 or 270 degrees.")

        if rotation:
            image = image.rotate(
                rotation,
                expand=True,
                resample=Image.Resampling.BICUBIC,
            )

        if flip_horizontal:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        if flip_vertical:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)

        if crop_x < 0 or crop_y < 0:
            raise ValueError("Crop coordinates must be non-negative.")
        if crop_width <= 0 or crop_height <= 0:
            raise ValueError("Crop dimensions must be positive.")
        if crop_x + crop_width > image.width:
            raise ValueError("Crop area extends beyond the right edge.")
        if crop_y + crop_height > image.height:
            raise ValueError("Crop area extends beyond the bottom edge.")

        image = image.crop(
            (crop_x, crop_y, crop_x + crop_width, crop_y + crop_height)
        )

        if output_format == "auto":
            fmt_map = {
                "JPEG": "jpg",
                "JPG": "jpg",
                "PNG": "png",
                "WEBP": "webp",
            }
            output_format = fmt_map.get(input_format, "png")

        output_format = output_format.lower()
        if output_format not in SUPPORTED_OUTPUT_FORMATS:
            raise ValueError(
                f"Unsupported output format: {output_format}. "
                "Use auto, jpg, png or webp."
            )

        image, flattened = prepare_for_output(
            image,
            output_format,
            background_color,
        )

        if output_format in ("jpg", "jpeg") and quality is None:
            quality = 90
        elif output_format == "webp" and quality is None:
            quality = 95

        data, content_type = pillow_adapter.encode(
            image,
            output_format,
            quality=quality or 92,
            strip_metadata=strip_metadata,
            background_color=background_color,
        )

        tool_logger.info(
            "cropped %dx%d -> %dx%d (%d -> %d bytes) in %.2fs",
            original_width,
            original_height,
            image.width,
            image.height,
            original_size,
            len(data),
            time.monotonic() - started,
        )
        return {
            "data": data,
            "content_type": content_type,
            "extension": "jpg" if output_format in ("jpg", "jpeg") else output_format,
            "width": image.width,
            "height": image.height,
            "input_format": input_format,
            "original_width": original_width,
            "original_height": original_height,
            "original_size": original_size,
            "output_size": len(data),
            "flattened": flattened,
            "has_alpha": has_transparency(image) if not flattened else False,
        }


image_cropper_service = ImageCropperService()
