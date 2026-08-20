"""QR code generation for the qr-generator tool."""

import time
from io import BytesIO

from PIL import Image

from app.core.logging import get_tool_logger


class QrService:
    """Generate QR codes with optional logo overlay."""

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
        tool_logger = get_tool_logger("qr-generator")
        started = time.monotonic()
        import qrcode

        if not content.strip():
            raise ValueError("QR code content cannot be empty.")

        if output_format == "svg":
            return self._make_svg(
                content, box_size, border, fill_color, back_color, started, tool_logger
            )

        factory = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        factory.add_data(content)
        factory.make(fit=True)
        img = factory.make_image(
            fill_color=fill_color,
            back_color=back_color,
        ).convert("RGBA")

        if image_data is not None:
            img = self._overlay_logo(img, image_data)

        buffer = BytesIO()
        if output_format == "webp":
            img.save(buffer, format="WEBP", quality=95)
            tool_logger.info(
                "generated qr (webp, %d bytes) in %.2fs",
                buffer.getbuffer().nbytes,
                time.monotonic() - started,
            )
            return buffer.getvalue(), "image/webp"
        img.save(buffer, format="PNG")
        tool_logger.info(
            "generated qr (png, %d bytes) in %.2fs",
            buffer.getbuffer().nbytes,
            time.monotonic() - started,
        )
        return buffer.getvalue(), "image/png"

    @staticmethod
    def _make_svg(
        content: str,
        box_size: int,
        border: int,
        fill_color: str,
        back_color: str,
        started: float,
        tool_logger,
    ) -> tuple[bytes, str]:
        import qrcode
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
        tool_logger.info(
            "generated qr (svg, %d bytes) in %.2fs",
            buffer.getbuffer().nbytes,
            time.monotonic() - started,
        )
        return buffer.getvalue(), "image/svg+xml"

    @staticmethod
    def _overlay_logo(img: Image.Image, image_data: bytes) -> Image.Image:
        try:
            logo = Image.open(BytesIO(image_data))
            logo.load()
        except Exception as error:
            raise ValueError("The uploaded logo is not a valid image.") from error
        logo = logo.convert("RGBA")
        box = img.size[0] // 5
        logo.thumbnail((box, box), Image.Resampling.LANCZOS)
        pos = ((img.size[0] - logo.width) // 2, (img.size[1] - logo.height) // 2)
        img.paste(logo, pos, logo)
        return img


qr_service = QrService()
