"""PDF rotate service."""

import time
from io import BytesIO

import pikepdf

from app.core.logging import get_tool_logger
from app.modules.pdf.services.pdf_page_utils import (
    parse_page_selection,
)


class PdfRotateService:

    def rotate(
        self,
        file_data: bytes,
        angle: int,
        pages_spec: str = "all",
    ) -> tuple[bytes, int]:
        tool_logger = get_tool_logger("pdf-rotator")
        started = time.monotonic()
        if angle not in (90, 180, 270):
            raise ValueError(
                "Rotation angle must be 90, 180 or 270."
            )
        with pikepdf.open(BytesIO(file_data)) as pdf:
            page_count = len(pdf.pages)
            if pages_spec == "all":
                targets = list(range(page_count))
            else:
                targets = [
                    page - 1
                    for page in parse_page_selection(
                        pages_spec,
                        page_count,
                    )
                ]
            for index in targets:
                pdf.pages[index].rotate(angle, relative=True)
            output_buffer = BytesIO()
            pdf.save(output_buffer)
        tool_logger.info(
            "rotated %d/%d pages by %d deg in %.2fs",
            len(targets),
            page_count,
            angle,
            time.monotonic() - started,
        )
        return output_buffer.getvalue(), page_count


pdf_rotate_service = PdfRotateService()
