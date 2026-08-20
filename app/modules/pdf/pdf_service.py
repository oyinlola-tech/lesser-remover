"""Facade over the per-tool PDF services."""

from app.modules.pdf.services.pdf_encrypt_service import (
    pdf_encrypt_service,
)
from app.modules.pdf.services.pdf_extract_service import (
    pdf_extract_service,
)
from app.modules.pdf.services.pdf_from_images_service import (
    pdf_from_images_service,
)
from app.modules.pdf.services.pdf_merge_service import (
    pdf_merge_service,
)
from app.modules.pdf.services.pdf_page_count_service import (
    pdf_page_count_service,
)
from app.modules.pdf.services.pdf_page_number_service import (
    pdf_page_number_service,
)
from app.modules.pdf.services.pdf_page_utils import (
    parse_page_selection,
)
from app.modules.pdf.services.pdf_rotate_service import (
    pdf_rotate_service,
)
from app.modules.pdf.services.pdf_split_service import (
    pdf_split_service,
)
from app.modules.pdf.services.pdf_to_image_service import (
    pdf_to_image_service,
)
from app.modules.pdf.services.pdf_watermark_service import (
    pdf_watermark_service,
)


class PdfService:

    def page_count(
        self,
        file_data: bytes,
    ) -> int:
        return pdf_page_count_service.page_count(file_data)

    def merge(
        self,
        files: list[tuple[str, bytes]],
    ) -> tuple[bytes, int]:
        return pdf_merge_service.merge(files)

    def split(
        self,
        file_data: bytes,
        filename: str,
    ) -> tuple[bytes, list[str]]:
        return pdf_split_service.split(file_data, filename)

    def rotate(
        self,
        file_data: bytes,
        angle: int,
        pages_spec: str = "all",
    ) -> tuple[bytes, int]:
        return pdf_rotate_service.rotate(file_data, angle, pages_spec)

    def extract_pages(
        self,
        file_data: bytes,
        pages_spec: str,
        filename: str,
    ) -> tuple[bytes, list[str]]:
        return pdf_extract_service.extract_pages(
            file_data,
            pages_spec,
            filename,
        )

    def to_images(
        self,
        file_data: bytes,
        image_format: str = "png",
        dpi: int = 150,
    ) -> list[tuple[str, bytes]]:
        return pdf_to_image_service.to_images(
            file_data,
            image_format=image_format,
            dpi=dpi,
        )

    def from_images(
        self,
        images: list[tuple[str, bytes]],
    ) -> tuple[bytes, int]:
        return pdf_from_images_service.from_images(images)

    def encrypt(
        self,
        file_data: bytes,
        user_password: str,
        owner_password: str | None = None,
    ) -> tuple[bytes, int]:
        return pdf_encrypt_service.encrypt(
            file_data,
            user_password,
            owner_password,
        )

    def add_page_numbers(
        self,
        file_data: bytes,
        position: str = "bottom-right",
    ) -> tuple[bytes, int]:
        return pdf_page_number_service.add_page_numbers(
            file_data,
            position,
        )

    def add_watermark(
        self,
        file_data: bytes,
        text: str = "CONFIDENTIAL",
    ) -> tuple[bytes, int]:
        return pdf_watermark_service.add_watermark(
            file_data,
            text,
        )


pdf_service = PdfService()

_parse_page_selection = parse_page_selection
