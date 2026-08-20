"""HTTP-facing logic for the qr-generator tool."""

from fastapi import UploadFile

from app.modules.devtools.controllers.devtools_controller_helpers import (
    as_http_error,
    read_upload,
)
from app.modules.devtools.services.qr_service import qr_service


class QrController:
    async def qr(
        self,
        content: str,
        box_size: int = 10,
        border: int = 4,
        fill_color: str = "#163300",
        back_color: str = "#ffffff",
        output_format: str = "png",
        logo: UploadFile | None = None,
    ) -> tuple[bytes, str]:
        logo_data = await read_upload(logo, "logo")
        try:
            return qr_service.generate_qr(
                content,
                box_size=box_size,
                border=border,
                fill_color=fill_color,
                back_color=back_color,
                output_format=output_format,
                image_data=logo_data,
            )
        except (OSError, ValueError) as error:
            raise as_http_error("Unable to generate QR code", error) from error


qr_controller = QrController()
