from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from app.infrastructure.compression.pillow_adapter import (
    pillow_adapter,
)
from app.modules.image.image_processor import image_processor
from app.shared.utils.file_util import generate_filename

SUPPORTED_CONVERSION_FORMATS = {"jpg", "png", "webp", "avif"}

POSITION_ALIASES = {
    "top-left": ("left", "top"),
    "top-right": ("right", "top"),
    "bottom-left": ("left", "bottom"),
    "bottom-right": ("right", "bottom"),
    "center": ("center", "center"),
}


def _default_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


class ImageService:
    def generate_background_variants(
        self,
        image: Image.Image,
        original_filename: str,
    ) -> list[tuple[str, str, bytes]]:
        png_data = image_processor.create_png(
            image,
        )
        webp_data = image_processor.create_webp(
            image,
            quality=95,
        )
        png_filename = generate_filename(
            original_filename,
            extension="png",
        )
        webp_filename = generate_filename(
            original_filename,
            extension="webp",
        )
        return [
            (
                "png",
                png_filename,
                png_data,
            ),
            (
                "webp",
                webp_filename,
                webp_data,
            ),
        ]

    def _open(self, file_data: bytes) -> Image.Image:
        image = Image.open(BytesIO(file_data))
        image.load()
        return image

    def convert(
        self,
        file_data: bytes,
        output_format: str,
    ) -> dict:
        """Convert an image to another format.

        Returns encoded bytes plus a flag when transparency had to be
        flattened (e.g. RGBA -> JPEG), so the caller can inform the user.
        """
        output_format = output_format.lower()
        if output_format not in SUPPORTED_CONVERSION_FORMATS:
            raise ValueError(
                f"Unsupported output format: {output_format}. "
                "Use jpg, png, webp or avif."
            )
        image = self._open(file_data)
        flattened = False
        if output_format == "jpg" and image.mode in (
            "RGBA",
            "LA",
            "P",
        ):
            flattened = True
        data, content_type = pillow_adapter.encode(
            image,
            output_format,
        )
        return {
            "data": data,
            "content_type": content_type,
            "extension": "jpg" if output_format == "jpeg" else output_format,
            "width": image.width,
            "height": image.height,
            "flattened": flattened,
        }

    def resize(
        self,
        file_data: bytes,
        width: int | None = None,
        height: int | None = None,
        percent: float | None = None,
        max_dimension: int | None = None,
        output_format: str = "png",
        cover: bool = False,
    ) -> dict:
        """Resize an image, preserving aspect ratio whenever possible.

        Rules:
        - ``percent`` scales the whole image.
        - ``width``/``height`` may be given alone (aspect kept) or
          together (both honored, aspect not guaranteed).
        - ``max_dimension`` shrinks the longer edge to that value.
        - ``cover`` center-crops to fill the exact box (both width
          and height must be given).
        """
        image = self._open(file_data)
        original = image.size

        if cover and width is not None and height is not None:
            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive.")
            target_ratio = width / height
            source_ratio = image.width / image.height
            if source_ratio > target_ratio:
                crop_width = round(image.height * target_ratio)
                crop_height = image.height
            else:
                crop_width = image.width
                crop_height = round(image.width / target_ratio)
            left = (image.width - crop_width) // 2
            top = (image.height - crop_height) // 2
            image = image.crop(
                (
                    left,
                    top,
                    left + crop_width,
                    top + crop_height,
                )
            )
            new_size = (width, height)
        elif percent is not None:
            factor = percent / 100
            if factor <= 0:
                raise ValueError("Percentage must be greater than zero.")
            new_size = (
                max(1, round(image.width * factor)),
                max(1, round(image.height * factor)),
            )
        elif max_dimension is not None:
            if max_dimension <= 0:
                raise ValueError("Maximum dimension must be positive.")
            image.thumbnail(
                (max_dimension, max_dimension),
                Image.Resampling.LANCZOS,
            )
            new_size = image.size
        elif width is not None and height is not None:
            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive.")
            new_size = (width, height)
        elif width is not None:
            if width <= 0:
                raise ValueError("Width must be positive.")
            ratio = width / image.width
            new_size = (
                width,
                max(1, round(image.height * ratio)),
            )
        elif height is not None:
            if height <= 0:
                raise ValueError("Height must be positive.")
            ratio = height / image.height
            new_size = (
                max(1, round(image.width * ratio)),
                height,
            )
        else:
            raise ValueError(
                "Provide width, height, percentage or max dimension."
            )

        resized = image.resize(
            new_size,
            Image.Resampling.LANCZOS,
        )
        data, content_type = pillow_adapter.encode(
            resized,
            output_format,
        )
        return {
            "data": data,
            "content_type": content_type,
            "extension": output_format,
            "width": resized.width,
            "height": resized.height,
            "original_width": original[0],
            "original_height": original[1],
        }

    def remove_metadata(
        self,
        file_data: bytes,
    ) -> dict:
        """Re-encode the image, dropping EXIF/GPS/camera metadata.

        Explicit operation: callers only invoke it when the user asked
        for metadata removal.
        """
        image = self._open(file_data)
        source_format = (
            image.format or "png"
        ).upper()
        removed = [
            key
            for key in (
                "exif",
                "gps",
                "dpi",
                "icc_profile",
                "comment",
                "photoshop",
            )
            if key in image.info
        ]
        if source_format == "JPEG":
            data = pillow_adapter.encode_jpeg(
                image,
                quality=95,
            )
            content_type = "image/jpeg"
            extension = "jpg"
        elif source_format == "WEBP":
            data = pillow_adapter.encode_webp(
                image,
                quality=95,
            )
            content_type = "image/webp"
            extension = "webp"
        elif source_format == "PNG":
            data = pillow_adapter.encode_png(image)
            content_type = "image/png"
            extension = "png"
        else:
            data = pillow_adapter.encode_png(
                image.convert("RGBA")
            )
            content_type = "image/png"
            extension = "png"
        return {
            "data": data,
            "content_type": content_type,
            "extension": extension,
            "removed_metadata": removed,
            "width": image.width,
            "height": image.height,
        }

    def add_watermark(
        self,
        file_data: bytes,
        text: str | None = None,
        logo_data: bytes | None = None,
        position: str = "bottom-right",
        opacity: float = 0.7,
        size_ratio: float = 0.1,
        rotation: int = 0,
    ) -> dict:
        """Overlay a text or logo watermark onto an image."""
        image = self._open(file_data).convert("RGBA")
        layer = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0),
        )
        draw = ImageDraw.Draw(layer)

        if text:
            font_size = max(
                10,
                round(min(image.size) * size_ratio),
            )
            font = _default_font(font_size)
            text_layer = Image.new(
                "RGBA",
                layer.size,
                (0, 0, 0, 0),
            )
            text_draw = ImageDraw.Draw(text_layer)
            bbox = text_draw.textbbox(
                (0, 0),
                text,
                font=font,
            )
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (image.width - text_width) // 2
            y = (image.height - text_height) // 2
            text_draw.text(
                (x - bbox[0], y - bbox[1]),
                text,
                font=font,
                fill=(255, 255, 255, round(255 * opacity)),
            )
            if rotation:
                text_layer = text_layer.rotate(
                    rotation,
                    expand=True,
                    resample=Image.Resampling.BICUBIC,
                )
            layer = text_layer
        elif logo_data:
            try:
                logo = Image.open(BytesIO(logo_data))
                logo.load()
            except Exception as error:
                raise ValueError(
                    "The uploaded watermark logo is not a valid image."
                ) from error
            logo = logo.convert("RGBA")
            target = max(
                16,
                round(min(image.size) * size_ratio),
            )
            logo.thumbnail(
                (target, target),
                Image.Resampling.LANCZOS,
            )
            if logo.mode == "RGBA":
                alpha = logo.getchannel("A").point(
                    lambda value: round(value * opacity)
                )
                logo.putalpha(alpha)
            if rotation:
                logo = logo.rotate(
                    rotation,
                    expand=True,
                    resample=Image.Resampling.BICUBIC,
                )
            x = (image.width - logo.width) // 2
            y = (image.height - logo.height) // 2
            layer.paste(logo, (x, y), logo)
        else:
            raise ValueError("Provide watermark text or a logo image.")

        anchor = POSITION_ALIASES.get(position)
        if anchor is None:
            raise ValueError(f"Unknown watermark position: {position}")
        horizontal, vertical = anchor

        def place(watermark: Image.Image) -> Image.Image:
            canvas = Image.new(
                "RGBA",
                image.size,
                (0, 0, 0, 0),
            )
            margin = max(12, round(min(image.size) * 0.04))
            if horizontal == "left":
                x = margin
            elif horizontal == "right":
                x = image.width - watermark.width - margin
            else:
                x = (image.width - watermark.width) // 2
            if vertical == "top":
                y = margin
            elif vertical == "bottom":
                y = image.height - watermark.height - margin
            else:
                y = (image.height - watermark.height) // 2
            canvas.paste(watermark, (x, y), watermark)
            return canvas

        positioned = place(layer)
        result = Image.alpha_composite(image, positioned)
        data = pillow_adapter.encode_webp(
            result,
            quality=95,
        )
        return {
            "data": data,
            "content_type": "image/webp",
            "extension": "webp",
            "width": image.width,
            "height": image.height,
        }


image_service = ImageService()
