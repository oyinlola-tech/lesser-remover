"""HTTP-facing logic for the barcode-generator tool."""

from app.modules.devtools.controllers.devtools_controller_helpers import (
    as_http_error,
)
from app.modules.devtools.services.barcode_service import barcode_service


class BarcodeController:
    async def barcode(
        self,
        content: str,
        code_type: str = "code128",
        output_format: str = "png",
    ) -> tuple[bytes, str]:
        try:
            return barcode_service.generate_barcode(
                content,
                code_type=code_type,
                output_format=output_format,
            )
        except (OSError, ValueError) as error:
            raise as_http_error("Unable to generate barcode", error) from error


barcode_controller = BarcodeController()
