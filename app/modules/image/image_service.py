from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from app.core.config import settings
from app.infrastructure.compression.pillow_adapter import (
    pillow_adapter,
)
from app.modules.image.image_processor import image_processor
from app.shared.utils.file_util import generate_filename

SUPPORTED_CONVERSION_FORMATS = {"jpg", "png", "webp", "avif"}
SUPPORTED_RESIZE_FORMATS = {"jpg", "png", "webp"}
SUPPORTED_OUTPUT_FORMATS = {"auto", "jpg", "jpeg", "png", "webp"}

POSITION_ALIASES = {
    "top-left": ("left", "top"),
    "top-right": ("right", "top"),
    "bottom-left": ("left", "bottom"),
    "bottom-right": ("right", "bottom"),
    "center": ("center", "center"),
}


def _validate_dimensions(
    width: int | None,
    height: int | None,
    percent: float | None,
    max_dimension: int | None,
    resize_mode: str,
) -> None:
    """Validate resize parameters against configured limits."""
    max_w = settings.max_image_width
    max_h = settings.max_image_height
    max_px = settings.max_image_pixels

    if resize_mode not in {"aspect", "exact", "percent", "max"}:
        raise ValueError(
            f"Unknown resize mode: {resize_mode}. "
            "Use aspect, exact, percent or max."
        )

    if percent is not None:
        if percent <= 0:
            raise ValueError("Percentage must be greater than zero.")
        if percent > 10000:
            raise ValueError("Percentage is unreasonably large.")

    if width is not None and width <= 0:
        raise ValueError("Width must be positive.")
    if height is not None and height <= 0:
        raise ValueError("Height must be positive.")
    if max_dimension is not None and max_dimension <= 0:
        raise ValueError("Maximum dimension must be positive.")

    if width is not None and width > max_w:
        raise ValueError(
            f"Width exceeds maximum of {max_w} pixels."
        )
    if height is not None and height > max_h:
        raise ValueError(
            f"Height exceeds maximum of {max_h} pixels."
        )
    if max_dimension is not None and max_dimension > max(max_w, max_h):
        raise ValueError(
            f"Maximum dimension exceeds the allowed limit."
        )

    if width is not None and height is not None:
        if width * height > max_px:
            raise ValueError(
                f"Requested dimensions ({width}×{height}) exceed the "
                f"maximum pixel count of {max_px:,}."
            )


def _compute_new_size(
    src_w: int,
    src_h: int,
    resize_mode: str,
    width: int | None,
    height: int | None,
    percent: float | None,
    max_dimension: int | None,
    maintain_aspect_ratio: bool = True,
    allow_upscale: bool = False,
) -> tuple[int, int]:
    """Compute (new_w, new_h) from the requested resize parameters."""
    if resize_mode == "percent" and percent is not None:
        factor = percent / 100
        if factor <= 0:
            raise ValueError("Percentage must be greater than zero.")
        new_w = max(1, round(src_w * factor))
        new_h = max(1, round(src_h * factor))
        if not allow_upscale:
            new_w = min(new_w, src_w)
            new_h = min(new_h, src_h)
        return (new_w, new_h)

    if resize_mode == "max" and max_dimension is not None:
        if max_dimension <= 0:
            raise ValueError("Maximum dimension must be positive.")
        ratio = min(
            max_dimension / src_w if src_w else 1,
            max_dimension / src_h if src_h else 1,
        )
        if not allow_upscale:
            ratio = min(ratio, 1.0)
        new_w = max(1, round(src_w * ratio))
        new_h = max(1, round(src_h * ratio))
        return (new_w, new_h)

    if resize_mode == "exact" and width is not None and height is not None:
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")
        return (width, height)

    if resize_mode == "aspect":
        if maintain_aspect_ratio:
            if width is not None and height is not None:
                return (width, height)
            elif width is not None:
                if width <= 0:
                    raise ValueError("Width must be positive.")
                ratio = width / src_w
                new_h = max(1, round(src_h * ratio))
                if not allow_upscale:
                    new_w = min(width, src_w)
                    new_h = min(new_h, src_h)
                else:
                    new_w = width
                return (new_w, new_h)
            elif height is not None:
                if height <= 0:
                    raise ValueError("Height must be positive.")
                ratio = height / src_h
                new_w = max(1, round(src_w * ratio))
                if not allow_upscale:
                    new_h = min(height, src_h)
                    new_w = min(new_w, src_w)
                else:
                    new_h = height
                return (new_w, new_h)
            else:
                raise ValueError(
                    "Provide width or height when using aspect mode."
                )
        else:
            if width is not None and height is not None:
                if width <= 0 or height <= 0:
                    raise ValueError("Width and height must be positive.")
                return (width, height)
            elif width is not None:
                if width <= 0:
                    raise ValueError("Width must be positive.")
                return (width, src_h)
            elif height is not None:
                if height <= 0:
                    raise ValueError("Height must be positive.")
                return (src_w, height)
            else:
                raise ValueError(
                    "Provide width, height, percentage or max dimension."
                )

    raise ValueError(
        f"Invalid combination for mode '{resize_mode}'."
    )


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

    @staticmethod
    def _is_animated(image: Image.Image) -> bool:
        n_frames = getattr(image, "n_frames", 1)
        duration = image.info.get("duration")
        return n_frames > 1 or (duration is not None and isinstance(duration, list) and len(duration) > 1)

    @staticmethod
    def _has_transparency(image: Image.Image) -> bool:
        if image.mode in ("RGBA", "LA"):
            return True
        if image.mode == "P" and "transparency" in image.info:
            return True
        return False

    def _prepare_for_output(
        self,
        image: Image.Image,
        output_format: str,
        background_color: str | None,
    ) -> tuple[Image.Image, bool]:
        """Return (image, was_flattened) adjusting mode for output_format."""
        flattened = False

        if image.mode == "CMYK":
            image = image.convert("RGB")

        if output_format in ("jpg", "jpeg"):
            if self._has_transparency(image):
                from app.infrastructure.compression.pillow_adapter import _parse_color
                bg_color = _parse_color(background_color)
                background = Image.new("RGB", image.size, bg_color)
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(image, mask=image.getchannel("A"))
                image = background
                flattened = True
            elif image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

        return image, flattened

    def convert(
        self,
        file_data: bytes,
        output_format: str,
        quality: int | None = None,
        strip_metadata: bool = True,
        background_color: str | None = None,
        lossless: bool = False,
    ) -> dict:
        """Convert an image to another format.

        Returns encoded bytes plus metadata about the conversion,
        including whether transparency was flattened.
        """
        output_format = output_format.lower()
        if output_format not in SUPPORTED_CONVERSION_FORMATS:
            raise ValueError(
                f"Unsupported output format: {output_format}. "
                "Use jpg, png, webp or avif."
            )

        image = self._open(file_data)
        input_format = (image.format or "unknown").upper()

        if self._is_animated(image):
            raise ValueError("Animated images are not supported for conversion.")

        original_size = len(file_data)
        original_width = image.width
        original_height = image.height

        image, flattened = self._prepare_for_output(
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
            lossless=lossless,
            background_color=background_color,
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
            "has_alpha": self._has_transparency(image) if not flattened else False,
        }

    def resize(
        self,
        file_data: bytes,
        resize_mode: str = "aspect",
        width: int | None = None,
        height: int | None = None,
        percent: float | None = None,
        max_dimension: int | None = None,
        maintain_aspect_ratio: bool = True,
        allow_upscale: bool = False,
        output_format: str = "auto",
        quality: int | None = None,
        strip_metadata: bool = True,
        background_color: str | None = None,
    ) -> dict:
        """Resize an image with full control over dimensions and output.

        Modes:
        - ``aspect``:  maintain aspect ratio (width or height given)
        - ``exact``:   use exact width × height (aspect not guaranteed)
        - ``percent``: scale by percentage
        - ``max``:     fit within max_dimension × max_dimension

        ``output_format`` of ``"auto"`` preserves the source format when
        the chosen format is JPEG/PNG/WebP; otherwise defaults to PNG.
        """
        image = self._open(file_data)

        if self._is_animated(image):
            raise ValueError("Animated images are not supported for resizing.")

        input_format = (image.format or "unknown").upper()
        original_size = len(file_data)
        original_width = image.width
        original_height = image.height

        if image.mode == "CMYK":
            image = image.convert("RGB")

        _validate_dimensions(
            width,
            height,
            percent,
            max_dimension,
            resize_mode,
        )

        new_size = _compute_new_size(
            image.width,
            image.height,
            resize_mode,
            width,
            height,
            percent,
            max_dimension,
            maintain_aspect_ratio,
            allow_upscale,
        )

        if new_size == (image.width, image.height):
            resized = image.copy()
        elif new_size[0] <= 0 or new_size[1] <= 0:
            raise ValueError("Calculated dimensions are not positive.")
        else:
            resized = image.resize(
                new_size,
                Image.Resampling.LANCZOS,
            )

        if output_format == "auto":
            fmt_map = {
                "JPEG": "jpg",
                "JPG": "jpg",
                "PNG": "png",
                "WEBP": "webp",
                "AVIF": "avif",
            }
            output_format = fmt_map.get(input_format, "png")

        output_format = output_format.lower()
        if output_format not in SUPPORTED_RESIZE_FORMATS:
            raise ValueError(
                f"Unsupported output format for resize: {output_format}. "
                "Use jpg, png or webp."
            )

        resized, flattened = self._prepare_for_output(
            resized,
            output_format,
            background_color,
        )

        if output_format in ("jpg", "jpeg") and quality is None:
            quality = 90
        elif output_format == "webp" and quality is None:
            quality = 95

        data, content_type = pillow_adapter.encode(
            resized,
            output_format,
            quality=quality or 92,
            strip_metadata=strip_metadata,
            background_color=background_color,
        )

        return {
            "data": data,
            "content_type": content_type,
            "extension": "jpg" if output_format in ("jpg", "jpeg") else output_format,
            "width": resized.width,
            "height": resized.height,
            "input_format": input_format,
            "original_width": original_width,
            "original_height": original_height,
            "original_size": original_size,
            "output_size": len(data),
            "flattened": flattened,
            "has_alpha": self._has_transparency(resized) if not flattened else False,
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
