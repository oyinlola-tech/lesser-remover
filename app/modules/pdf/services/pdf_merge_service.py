"""PDF merge service."""

import time
from io import BytesIO

import pikepdf

from app.core.logging import get_tool_logger


class PdfMergeService:

    def merge(
        self,
        files: list[tuple[str, bytes]],
    ) -> tuple[bytes, int]:
        tool_logger = get_tool_logger("pdf-merger")
        started = time.monotonic()
        if len(files) < 2:
            raise ValueError(
                "At least two PDF files are required to merge."
            )
        output_buffer = BytesIO()
        with pikepdf.Pdf.new() as merged:
            for filename, file_data in files:
                try:
                    with pikepdf.open(
                        BytesIO(file_data),
                        password="",
                    ) as source:
                        merged.pages.extend(source.pages)
                except pikepdf.PdfError as error:
                    raise ValueError(
                        f"Invalid PDF file: {filename}"
                    ) from error
            merged.save(output_buffer)
        data = output_buffer.getvalue()
        page_count = len(list(pikepdf.open(BytesIO(data)).pages))
        tool_logger.info(
            "merged %d files into %d pages (%d bytes) in %.2fs",
            len(files),
            page_count,
            len(data),
            time.monotonic() - started,
        )
        return data, page_count


pdf_merge_service = PdfMergeService()
