"""Shared PIL color parsing and metadata filtering."""

from PIL.Image import Image
from PIL.PngImagePlugin import PngInfo


def parse_color(color) -> tuple[int, int, int] | str:
    """Parse a hex color string or PIL-compatible color into a usable value.

    Accepts ``"#ffffff"``, ``"ffffff"``, and plain PIL color names.
    """
    if color is None:
        return "white"
    if isinstance(color, str):
        cleaned = color.lstrip("#").lower()
        if len(cleaned) == 6:
            try:
                return (
                    int(cleaned[0:2], 16),
                    int(cleaned[2:4], 16),
                    int(cleaned[4:6], 16),
                )
            except ValueError:
                pass
        if cleaned in {"fff", "white"}:
            return (255, 255, 255)
        if cleaned in {"000", "black"}:
            return (0, 0, 0)
    return color


def filter_metadata(
    image: Image,
    strip: bool,
) -> dict:
    """Return save-kwargs for metadata.

    When ``strip`` is True, no EXIF/ICC/text chunks are embedded so the
    resulting file carries only pixel data.  When False, the common
    metadata keys are preserved when present.
    """
    if not strip:
        kwargs: dict = {}
        if image.info.get("exif"):
            kwargs["exif"] = image.info["exif"]
        if image.info.get("icc_profile"):
            kwargs["icc_profile"] = image.info["icc_profile"]
        png_info = PngInfo()
        preserved = False
        if image.info.get("pnginfo"):
            png_info = image.info["pnginfo"]
            preserved = True
        for key, value in image.info.items():
            if key in ("exif", "icc_profile", "pnginfo"):
                continue
            if isinstance(value, (str, bytes)):
                png_info.add_text(
                    key,
                    value if isinstance(value, str) else value.decode(
                        "utf-8",
                        errors="replace",
                    ),
                )
                preserved = True
        if preserved:
            kwargs["pnginfo"] = png_info
        return kwargs
    return {}
