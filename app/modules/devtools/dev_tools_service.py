from io import BytesIO
from xml.etree import ElementTree

from PIL import Image


def _favicon_sizes(image: Image.Image, size: int) -> Image.Image:
    source = image.convert("RGBA")
    if size <= 32:
        preview = source.copy()
        preview.thumbnail((size * 2, size * 2))
        return preview.resize(
            (size, size),
            Image.Resampling.LANCZOS,
        )
    target = source.copy()
    target.thumbnail(
        (size, size),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new(
        "RGBA",
        (size, size),
        (0, 0, 0, 0),
    )
    canvas.paste(
        target,
        ((size - target.width) // 2, (size - target.height) // 2),
    )
    return canvas


def _barcode_factory(code_type: str):
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
        raise ValueError(
            f"Unsupported barcode type: {code_type}"
        )
    try:
        return getattr(barcode, name)
    except AttributeError as error:
        raise ValueError(
            f"Unsupported barcode type: {code_type}"
        ) from error


class DevToolsService:
    def generate_favicon(
        self,
        image_data: bytes,
        size: int = 64,
        add_padding: bool = False,
    ) -> dict:
        """Create a favicon set (ICO + PNGs) from a source image."""
        source = Image.open(BytesIO(image_data))
        source.load()
        square = source.convert("RGBA")
        if square.width != square.height:
            side = min(square.size)
            square = square.crop(
                (
                    (square.width - side) // 2,
                    (square.height - side) // 2,
                    (square.width + side) // 2,
                    (square.height + side) // 2,
                )
            )
        if add_padding:
            pad = max(1, round(square.width * 0.1))
            canvas = Image.new(
                "RGBA",
                (square.width + pad * 2, square.height + pad * 2),
                (0, 0, 0, 0),
            )
            canvas.paste(square, (pad, pad))
            square = canvas
        if size not in (16, 32, 48, 64, 128, 180, 256):
            size = 64
        sizes = [16, 32, 48]
        if size > 48:
            sizes.append(size)
        ico_buffer = BytesIO()
        frames = [
            _favicon_sizes(square, item)
            for item in sizes
        ]
        frames[0].save(
            ico_buffer,
            format="ICO",
            sizes=[(item, item) for item in sizes],
            append_images=frames[1:],
        )
        png_buffer = BytesIO()
        _favicon_sizes(square, size).save(
            png_buffer,
            format="PNG",
        )
        return {
            "ico": ico_buffer.getvalue(),
            "png": png_buffer.getvalue(),
            "sizes": sizes,
        }

    def optimize_svg(
        self,
        svg_data: bytes,
        precision: int = 2,
    ) -> dict:
        """Minify an SVG while keeping it structurally valid.

        Uses safe text-level transforms (comment strip, whitespace
        collapse, numeric rounding) and verifies the result still
        parses as XML before returning it.
        """
        import re

        text = svg_data.decode("utf-8")

        def minify(raw: str) -> str:
            cleaned = re.sub(
                r"<!--.*?-->",
                "",
                raw,
                flags=re.DOTALL,
            )
            cleaned = re.sub(r">\s+<", "><", cleaned)
            cleaned = re.sub(
                r"\s+",
                " ",
                cleaned,
            ).strip()
            cleaned = cleaned.replace(" />", "/>")
            if precision is not None and precision >= 0:
                def round_number(match: re.Match) -> str:
                    try:
                        value = float(match.group(0))
                    except ValueError:
                        return match.group(0)
                    if value == int(value):
                        return str(int(value))
                    return format(value, f".{precision}f").rstrip("0").rstrip(".")
                cleaned = re.sub(
                    r"(?<![\w#])(-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)",
                    round_number,
                    cleaned,
                )
            return cleaned

        try:
            ElementTree.fromstring(svg_data)
        except ElementTree.ParseError as error:
            raise ValueError(
                f"Invalid SVG file: {error}"
            ) from error
        minified = minify(text)
        try:
            ElementTree.fromstring(minified.encode("utf-8"))
        except ElementTree.ParseError as error:
            raise ValueError(
                f"Minification produced invalid SVG: {error}"
            ) from error
        minified_bytes = minified.encode("utf-8")
        return {
            "data": minified_bytes,
            "original_size": len(svg_data),
            "minified_size": len(minified_bytes),
        }

    def generate_svg(
        self,
        image_data: bytes,
        threshold: int = 128,
        background_color: str = "white",
        foreground_color: str = "black",
    ) -> str:
        """Convert a raster image (PNG/JPG/WebP) to an SVG path.

        Uses potrace to trace the bitmap and produces a single
        ``<path>`` element per contiguous shape.  The image is
        converted to 1-bit black-and-white before tracing.

        Parameters
        ----------
        image_data
            Raw bytes of a supported raster image (PNG, JPEG, WebP).
        threshold
            Luminance value (0-255) below which a pixel is considered
            "foreground".  Higher values make tracing more sensitive.
        background_color
            Color name or hex code for the background rect.
        foreground_color
            Color name or hex code for the traced paths.
        """
        import numpy as np
        import potrace

        source = Image.open(BytesIO(image_data))
        source.load()
        grayscale = source.convert("L")
        bw = grayscale.point(
            lambda x: 0 if x < threshold else 255,
            mode="1",
        )
        bitmap = potrace.Bitmap(np.array(bw))
        path = bitmap.trace()

        w, h = source.width, source.height
        parts: list[str] = [
            '<svg xmlns="http://www.w3.org/2000/svg"',
            f' width="{w}" height="{h}"',
            f' viewBox="0 0 {w} {h}">',
        ]
        if background_color.lower() != "transparent":
            parts.append(
                f'<rect width="{w}" height="{h}" '
                f'fill="{background_color}"/>'
            )
        for curve in path:
            start = curve.start_point
            d = [f"M{start.x:.2f},{start.y:.2f}"]
            for seg in curve:
                end = seg.end_point
                if seg.is_corner:
                    d.append(
                        f"L{end.x:.2f},{end.y:.2f}"
                    )
                else:
                    d.append(
                        f"C{seg.c1.x:.2f},{seg.c1.y:.2f}"
                        f" {seg.c2.x:.2f},{seg.c2.y:.2f}"
                        f" {end.x:.2f},{end.y:.2f}"
                    )
            d.append("Z")
            parts.append(
                f'<path fill="{foreground_color}" '
                f'd="{" ".join(d)}"/>'
            )
        parts.append("</svg>")
        return "".join(parts)

    def generate_qr(
        self,
        content: str,
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "#163300",
        back_color: str = "#ffffff",
        output_format: str = "png",
        image_data: bytes | None = None,
    ) -> tuple[bytes, str]:
        import qrcode

        if not content.strip():
            raise ValueError("QR code content cannot be empty.")
        factory = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        factory.add_data(content)
        factory.make(fit=True)
        if image_data is not None:
            try:
                logo = Image.open(BytesIO(image_data))
                logo.load()
            except Exception as error:
                raise ValueError(
                    "The uploaded logo is not a valid image."
                ) from error
            logo = logo.convert("RGBA")
            img = factory.make_image(
                fill_color=fill_color,
                back_color=back_color,
            ).convert("RGBA")
            box = img.size[0] // 5
            logo.thumbnail((box, box), Image.Resampling.LANCZOS)
            pos = ((img.size[0] - logo.width) // 2, (img.size[1] - logo.height) // 2)
            img.paste(logo, pos, logo)
        else:
            img = factory.make_image(
                fill_color=fill_color,
                back_color=back_color,
            ).convert("RGBA")
        if output_format == "svg":
            import qrcode.image.svg

            factory = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=box_size,
                border=border,
            )
            factory.add_data(content)
            factory.make(fit=True)
            svg_img = factory.make_image(
                image_factory=qrcode.image.svg.SvgPathImage,
                fill_color=fill_color,
                back_color=back_color,
            )
            buffer = BytesIO()
            svg_img.save(buffer)
            return buffer.getvalue(), "image/svg+xml"
        buffer = BytesIO()
        if output_format == "webp":
            img.save(buffer, format="WEBP", quality=95)
            return buffer.getvalue(), "image/webp"
        img.save(buffer, format="PNG")
        return buffer.getvalue(), "image/png"

    def generate_barcode(
        self,
        content: str,
        code_type: str = "code128",
        output_format: str = "png",
    ) -> tuple[bytes, str]:
        if not content.strip():
            raise ValueError("Barcode content cannot be empty.")
        cls = _barcode_factory(code_type)
        writer_options = {
            "module_width": 0.4,
            "module_height": 20,
            "font_size": 14,
            "text_distance": 3,
            "quiet_zone": 6,
        }
        if output_format == "svg":
            from barcode.writer import SVGWriter

            try:
                instance = cls(
                    content,
                    writer=SVGWriter(),
                )
            except Exception as error:
                raise ValueError(
                    f"Unable to encode '{content}' as "
                    f"{code_type}: {error}"
                ) from error
            data = instance.render(
                writer_options={
                    **writer_options,
                    "write_text": True,
                }
            )
            return data, "image/svg+xml"
        from barcode.writer import ImageWriter

        try:
            instance = cls(
                content,
                writer=ImageWriter(),
            )
            image = instance.render(
                writer_options=writer_options,
            )
        except Exception as error:
            raise ValueError(
                f"Unable to render barcode: {error}"
            ) from error
        buffer = BytesIO()
        if output_format == "webp":
            image.convert("RGB").save(
                buffer,
                format="WEBP",
                quality=95,
            )
            return buffer.getvalue(), "image/webp"
        image.save(buffer, format="PNG")
        return buffer.getvalue(), "image/png"


dev_tools_service = DevToolsService()
