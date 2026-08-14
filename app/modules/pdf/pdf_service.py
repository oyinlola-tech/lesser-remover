from io import BytesIO

import pikepdf
from PIL import Image

from app.infrastructure.archive.zip_adapter import zip_adapter
from app.infrastructure.compression.ghostscript_adapter import (
    ghostscript_adapter,
)


def _parse_page_selection(spec: str, page_count: int) -> list[int]:
    """Parse a page selection like '1,3-5' into 1-based page numbers."""
    selection: list[int] = []
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start, end = token.split("-", 1)
            start = int(start.strip())
            end = int(end.strip())
            if start < 1 or end > page_count or start > end:
                raise ValueError(
                    f"Invalid page range: {token}"
                )
            selection.extend(range(start, end + 1))
        else:
            page = int(token)
            if page < 1 or page > page_count:
                raise ValueError(
                    f"Invalid page number: {token}"
                )
            selection.append(page)
    selection = sorted(set(selection))
    if not selection:
        raise ValueError("Page selection is empty.")
    return selection


class PdfService:
    def page_count(
        self,
        file_data: bytes,
    ) -> int:
        with pikepdf.open(BytesIO(file_data)) as pdf:
            return len(pdf.pages)

    def merge(
        self,
        files: list[tuple[str, bytes]],
    ) -> tuple[bytes, int]:
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
        return data, len(list(pikepdf.open(BytesIO(data)).pages))

    def split(
        self,
        file_data: bytes,
        filename: str,
    ) -> tuple[bytes, list[str]]:
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
        return zip_adapter.create_archive(entries), [
            name for name, _ in entries
        ]

    def rotate(
        self,
        file_data: bytes,
        angle: int,
        pages_spec: str = "all",
    ) -> tuple[bytes, int]:
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
                    for page in _parse_page_selection(
                        pages_spec,
                        page_count,
                    )
                ]
            for index in targets:
                pdf.pages[index].rotate(angle, relative=True)
            output_buffer = BytesIO()
            pdf.save(output_buffer)
        return output_buffer.getvalue(), page_count

    def extract_pages(
        self,
        file_data: bytes,
        pages_spec: str,
        filename: str,
    ) -> tuple[bytes, list[str]]:
        with pikepdf.open(BytesIO(file_data)) as pdf:
            page_count = len(pdf.pages)
            targets = _parse_page_selection(pages_spec, page_count)
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
        return zip_adapter.create_archive(entries), [
            name for name, _ in entries
        ]

    def to_images(
        self,
        file_data: bytes,
        image_format: str = "png",
        dpi: int = 150,
    ) -> tuple[bytes, list[str]]:
        image_format = image_format.lower()
        if image_format not in {"png", "jpeg"}:
            raise ValueError(
                "Image format must be png or jpeg."
            )
        if dpi < 50 or dpi > 600:
            raise ValueError(
                "DPI must be between 50 and 600."
            )
        pages = ghostscript_adapter.to_images(
            file_data,
            image_format=image_format,
            dpi=dpi,
        )
        return zip_adapter.create_archive(pages), [
            name for name, _ in pages
        ]

    def from_images(
        self,
        images: list[tuple[str, bytes]],
    ) -> tuple[bytes, int]:
        if not images:
            raise ValueError("No images were provided.")
        first = Image.open(BytesIO(images[0][1]))
        first.load()
        if first.mode in ("RGBA", "LA", "P"):
            first = first.convert("RGB")
        pages = [first]
        for _, data in images[1:]:
            image = Image.open(BytesIO(data))
            image.load()
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGB")
            pages.append(image)
        output_buffer = BytesIO()
        pages[0].save(
            output_buffer,
            format="PDF",
            save_all=True,
            append_images=pages[1:],
            resolution=150,
        )
        data = output_buffer.getvalue()
        return data, len(pages)


pdf_service = PdfService()
