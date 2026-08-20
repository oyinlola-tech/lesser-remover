"""Facade over the per-tool PDF controllers."""

from app.modules.pdf.controllers.pdf_encrypt_controller import (
    pdf_encrypt_controller,
)
from app.modules.pdf.controllers.pdf_extract_controller import (
    pdf_extract_controller,
)
from app.modules.pdf.controllers.pdf_from_images_controller import (
    pdf_from_images_controller,
)
from app.modules.pdf.controllers.pdf_info_controller import (
    pdf_info_controller,
)
from app.modules.pdf.controllers.pdf_merge_controller import (
    pdf_merge_controller,
)
from app.modules.pdf.controllers.pdf_page_number_controller import (
    pdf_page_number_controller,
)
from app.modules.pdf.controllers.pdf_rotate_controller import (
    pdf_rotate_controller,
)
from app.modules.pdf.controllers.pdf_split_controller import (
    pdf_split_controller,
)
from app.modules.pdf.controllers.pdf_to_images_controller import (
    pdf_to_images_controller,
)
from app.modules.pdf.controllers.pdf_watermark_controller import (
    pdf_watermark_controller,
)


class PdfController:

    async def merge(self, files):
        return await pdf_merge_controller.merge(files)

    async def split(self, file):
        return await pdf_split_controller.split(file)

    async def rotate(self, file, angle, pages_spec):
        return await pdf_rotate_controller.rotate(file, angle, pages_spec)

    async def extract_pages(self, file, pages_spec):
        return await pdf_extract_controller.extract_pages(file, pages_spec)

    async def to_images(self, file, image_format, dpi, as_zip=False):
        return await pdf_to_images_controller.to_images(
            file,
            image_format,
            dpi,
            as_zip,
        )

    async def from_images(self, files):
        return await pdf_from_images_controller.from_images(files)

    async def info(self, file):
        return await pdf_info_controller.info(file)

    async def encrypt(self, file, user_password, owner_password=None):
        return await pdf_encrypt_controller.encrypt(
            file,
            user_password,
            owner_password,
        )

    async def page_number(self, file, position="bottom-right"):
        return await pdf_page_number_controller.page_number(file, position)

    async def watermark(self, file, text="CONFIDENTIAL"):
        return await pdf_watermark_controller.watermark(file, text)


pdf_controller = PdfController()
