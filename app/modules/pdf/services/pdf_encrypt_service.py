"""PDF encryption service."""

import time
from io import BytesIO

import pikepdf

from app.core.logging import get_tool_logger


class PdfEncryptService:

    def encrypt(
        self,
        file_data: bytes,
        user_password: str,
        owner_password: str | None = None,
    ) -> tuple[bytes, int]:
        tool_logger = get_tool_logger("pdf-encrypt")
        started = time.monotonic()
        if not user_password:
            raise ValueError("User password is required.")
        output_buffer = BytesIO()
        with pikepdf.open(BytesIO(file_data)) as pdf:
            page_count = len(pdf.pages)
            encryption = pikepdf.Encryption(
                user=user_password,
                owner=owner_password or user_password,
                R=6,
            )
            pdf.save(output_buffer, encryption=encryption)
        data = output_buffer.getvalue()
        tool_logger.info(
            "encrypted PDF (%d pages, %d bytes) in %.2fs",
            page_count,
            len(data),
            time.monotonic() - started,
        )
        return data, page_count


pdf_encrypt_service = PdfEncryptService()
