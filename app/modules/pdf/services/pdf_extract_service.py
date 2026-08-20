"""PDF page extraction service."""

import time
from io import BytesIO

import pikepdf

from app.core.logging import get_tool_logger
from app.infrastructure.archive.zip_adapter import zip_adapter
from app.modules.pdf.services.pdf_page_utils import (
    parse_page_selection,
)


class PdfExtractService:

    def extract_pages(
        self,
        file_data: bytes,
        pages_spec: str,
        filename: str,
    ) -> tuple[bytes, list[str]]:
        tool_logger = get_tool_logger("pdf-extractor")
        started = time.monotonic()
        with pikepdf.open(BytesIO(file_data)) as pdf:
            page_count = len(pdf.pages)
            targets = parse_page_selection(pages_spec, page_count)
            base_name = filename.rsplit(".", 1)[0]
            entries: list[tuple[str, bytes]] = []
            for page_number in targets:
                page_buffer = BytesIO()
                with pikepdf.Pdf.new() as single:
                    single.pages.append(pdf.pages[page_number - 1])
                    single.save(page_buffer)
                entries.append(
                    (
                        f"{base_name}-page-{page_number}.pdf",
                        page_buffer.getvalue(),
                    )
                )
        archive = zip_adapter.create_archive(entries)
        tool_logger.info(
            "extracted %d pages from %s in %.2fs",
            len(entries),
            filename,
            time.monotonic() - started,
        )
        return archive, [name for name, _ in entries]


pdf_extract_service = PdfExtractService()
