from dataclasses import dataclass

from app.shared.file_inspection.file_types import (
    FileCategory,
)


@dataclass(frozen=True)
class FileInspectionResult:
    category: FileCategory
    mime_type: str
    extension: str
    is_supported: bool


FILE_SIGNATURES = {
    b"\xFF\xD8\xFF": (
        FileCategory.IMAGE,
        "image/jpeg",
        ".jpg",
    ),
    b"\x89PNG\r\n\x1a\n": (
        FileCategory.IMAGE,
        "image/png",
        ".png",
    ),
    b"GIF87a": (
        FileCategory.IMAGE,
        "image/gif",
        ".gif",
    ),
    b"GIF89a": (
        FileCategory.IMAGE,
        "image/gif",
        ".gif",
    ),
    b"BM": (
        FileCategory.IMAGE,
        "image/bmp",
        ".bmp",
    ),
    b"%PDF-": (
        FileCategory.PDF,
        "application/pdf",
        ".pdf",
    ),
}


class FileInspector:
    def inspect(
        self,
        file_data: bytes,
    ) -> FileInspectionResult:
        if not file_data:
            return FileInspectionResult(
                category=FileCategory.UNKNOWN,
                mime_type="application/octet-stream",
                extension="",
                is_supported=False,
            )

        for signature, (
            category,
            mime_type,
            extension,
        ) in FILE_SIGNATURES.items():
            if file_data.startswith(signature):
                return FileInspectionResult(
                    category=category,
                    mime_type=mime_type,
                    extension=extension,
                    is_supported=True,
                )

        if (
            file_data.startswith(b"RIFF")
            and len(file_data) >= 12
            and file_data[8:12] == b"WEBP"
        ):
            return FileInspectionResult(
                category=FileCategory.IMAGE,
                mime_type="image/webp",
                extension=".webp",
                is_supported=True,
            )

        return FileInspectionResult(
            category=FileCategory.UNKNOWN,
            mime_type="application/octet-stream",
            extension="",
            is_supported=False,
        )


file_inspector = FileInspector()
