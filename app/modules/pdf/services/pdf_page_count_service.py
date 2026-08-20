"""PDF page count service."""

from io import BytesIO

import pikepdf


class PdfPageCountService:

    def page_count(
        self,
        file_data: bytes,
    ) -> int:
        with pikepdf.open(BytesIO(file_data)) as pdf:
            return len(pdf.pages)


pdf_page_count_service = PdfPageCountService()
