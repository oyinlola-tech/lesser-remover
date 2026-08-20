"""PDF split service."""

import time
from io import BytesIO

import pikepdf

from app.core.logging import get_tool_logger
from app.infrastructure.archive.zip_adapter import zip_adapter


class PdfSplitService:

    def split(
        self,
        file_data: bytes,
        filename: str,
    ) -> tuple[bytes, list[str]]:
        tool_logger = get_tool_logger("pdf-splitter")
        started = time.monotonic()
        with pikepdf.open(BytesIO(file_data)) as pdf:
            if len(pdf.pages) < 1:
                raise ValueError("The PDF has no pages.")
            base_name = filename.rsplit(".", 1)[0]
            entries: list[tuple[str, bytes]] = []
            for index, page in enumerate(pdf.pages, start=1):
                page_buffer = BytesIO()
                with pikepdf.Pdf.new() as single:
                    single.pages.append(page)
                    single.save(page_buffer)
                entries.append(
                    (
                        f"{base_name}-page-{index}.pdf",
                        page_buffer.getvalue(),
                    )
                )
        archive = zip_adapter.create_archive(entries)
        tool_logger.info(
            "split %s into %d pages (%d bytes archive) in %.2fs",
            filename,
            len(entries),
            len(archive),
            time.monotonic() - started,
        )
        return archive, [name for name, _ in entries]


pdf_split_service = PdfSplitService()
