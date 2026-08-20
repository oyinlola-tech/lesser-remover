"""Shared resize math for the image-resizer tool."""

from app.core.config import settings


def validate_dimensions(
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
        raise ValueError(f"Width exceeds maximum of {max_w} pixels.")
    if height is not None and height > max_h:
        raise ValueError(f"Height exceeds maximum of {max_h} pixels.")
    if max_dimension is not None and max_dimension > max(max_w, max_h):
        raise ValueError("Maximum dimension exceeds the allowed limit.")

    if width is not None and height is not None and width * height > max_px:
        raise ValueError(
            f"Requested dimensions ({width}x{height}) exceed the "
            f"maximum pixel count of {max_px:,}."
        )


def compute_new_size(
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
        return _percent_size(src_w, src_h, percent, allow_upscale)

    if resize_mode == "max" and max_dimension is not None:
        return _max_size(src_w, src_h, max_dimension, allow_upscale)

    if resize_mode == "exact" and width is not None and height is not None:
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")
        return (width, height)

    if resize_mode == "aspect":
        return _aspect_size(
            src_w, src_h, width, height, maintain_aspect_ratio, allow_upscale
        )

    raise ValueError(f"Invalid combination for mode '{resize_mode}'.")


def _percent_size(
    src_w: int, src_h: int, percent: float, allow_upscale: bool
) -> tuple[int, int]:
    factor = percent / 100
    if factor <= 0:
        raise ValueError("Percentage must be greater than zero.")
    new_w = max(1, round(src_w * factor))
    new_h = max(1, round(src_h * factor))
    if not allow_upscale:
        new_w = min(new_w, src_w)
        new_h = min(new_h, src_h)
    return (new_w, new_h)


def _max_size(
    src_w: int, src_h: int, max_dimension: int, allow_upscale: bool
) -> tuple[int, int]:
    if max_dimension <= 0:
        raise ValueError("Maximum dimension must be positive.")
    ratio = min(
        max_dimension / src_w if src_w else 1,
        max_dimension / src_h if src_h else 1,
    )
    if not allow_upscale:
        ratio = min(ratio, 1.0)
    return (max(1, round(src_w * ratio)), max(1, round(src_h * ratio)))


def _aspect_size(
    src_w: int,
    src_h: int,
    width: int | None,
    height: int | None,
    maintain_aspect_ratio: bool,
    allow_upscale: bool,
) -> tuple[int, int]:
    if width is not None and height is not None:
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")
        return (width, height)
    if width is not None:
        if width <= 0:
            raise ValueError("Width must be positive.")
        ratio = width / src_w
        new_h = max(1, round(src_h * ratio))
        new_w = min(width, src_w) if not allow_upscale else width
        return (new_w, min(new_h, src_h) if not allow_upscale else new_h)
    if height is not None:
        if height <= 0:
            raise ValueError("Height must be positive.")
        ratio = height / src_h
        new_w = max(1, round(src_w * ratio))
        new_h = min(height, src_h) if not allow_upscale else height
        return (min(new_w, src_w) if not allow_upscale else new_w, new_h)
    raise ValueError("Provide width or height when using aspect mode.")
