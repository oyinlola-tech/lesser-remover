"""Shared helpers for the devtools services."""

from PIL import Image


def favicon_sizes(image: Image.Image, size: int) -> Image.Image:
    source = image.convert("RGBA")
    if size <= 32:
        preview = source.copy()
        preview.thumbnail((size * 2, size * 2))
        return preview.resize((size, size), Image.Resampling.LANCZOS)
    target = source.copy()
    target.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(
        target,
        ((size - target.width) // 2, (size - target.height) // 2),
    )
    return canvas


def barcode_factory(code_type: str):
    import barcode

    name = {
        "code128": "Code128",
        "ean13": "EAN13",
        "ean8": "EAN8",
        "upca": "UPCA",
        "code39": "Code39",
        "itf": "ITF",
    }.get(code_type)
    if name is None:
        raise ValueError(f"Unsupported barcode type: {code_type}")
    try:
        return getattr(barcode, name)
    except AttributeError as error:
        raise ValueError(f"Unsupported barcode type: {code_type}") from error
