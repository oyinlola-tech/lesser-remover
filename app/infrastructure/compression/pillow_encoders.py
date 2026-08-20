"""PIL format encoders."""

from io import BytesIO

from PIL import Image

from app.infrastructure.compression.pillow_utils import (
    filter_metadata,
    parse_color,
)


def encode_png(
    image: Image.Image,
    strip_metadata: bool = True,
) -> bytes:
    output = BytesIO()
    try:
        save_kwargs = filter_metadata(image, strip=strip_metadata)
        image.save(
            output,
            format="PNG",
            optimize=True,
            **save_kwargs,
        )
        return output.getvalue()
    finally:
        output.close()


def encode_webp(
    image: Image.Image,
    quality: int = 95,
    strip_metadata: bool = True,
    lossless: bool = False,
) -> bytes:
    output = BytesIO()
    try:
        save_kwargs = filter_metadata(image, strip=strip_metadata)
        if lossless:
            image.save(
                output,
                format="WEBP",
                lossless=True,
                **save_kwargs,
            )
        else:
            image.save(
                output,
                format="WEBP",
                quality=quality,
                method=6,
                **save_kwargs,
            )
        return output.getvalue()
    finally:
        output.close()


def encode_jpeg(
    image: Image.Image,
    quality: int = 95,
    strip_metadata: bool = True,
    background_color: str | None = None,
) -> bytes:
    if image.mode in ("RGBA", "LA", "P"):
        bg = parse_color(background_color)
        background = Image.new("RGB", image.size, bg)
        if image.mode == "P":
            image = image.convert("RGBA")
        background.paste(image, mask=image.getchannel("A"))
        image = background
    elif image.mode != "RGB":
        image = image.convert("RGB")
    output = BytesIO()
    try:
        save_kwargs = filter_metadata(image, strip=strip_metadata)
        image.save(
            output,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True,
            **save_kwargs,
        )
        return output.getvalue()
    finally:
        output.close()


def encode_avif(
    image: Image.Image,
    quality: int = 85,
    strip_metadata: bool = True,
) -> bytes:
    if image.mode not in ("RGBA", "RGB", "LA"):
        image = image.convert("RGBA")
    output = BytesIO()
    try:
        save_kwargs = filter_metadata(image, strip=strip_metadata)
        image.save(
            output,
            format="AVIF",
            quality=quality,
            **save_kwargs,
        )
        return output.getvalue()
    finally:
        output.close()
