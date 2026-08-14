from io import BytesIO

from PIL import Image

from app.infrastructure.archive.zip_adapter import zip_adapter
from app.shared.file_inspection.file_inspector import (
    file_inspector,
)
from app.shared.utils.hash_util import sha256_hex


class FileToolsService:
    def analyze(
        self,
        files: list[tuple[str, bytes]],
    ) -> list[dict]:
        results: list[dict] = []
        for filename, file_data in files:
            inspection = file_inspector.inspect(file_data)
            result = {
                "filename": filename,
                "size_bytes": len(file_data),
                "mime_type": inspection.mime_type,
                "category": inspection.category.value,
                "extension": inspection.extension,
                "sha256": sha256_hex(file_data),
            }
            if inspection.category.value == "image":
                try:
                    image = Image.open(BytesIO(file_data))
                    result["width"] = image.width
                    result["height"] = image.height
                except OSError:
                    pass
            if inspection.category.value == "pdf":
                try:
                    import pikepdf

                    with pikepdf.open(
                        BytesIO(file_data),
                        password="",
                    ) as pdf:
                        result["page_count"] = len(pdf.pages)
                except Exception:
                    pass
            results.append(result)
        return results

    def create_zip(
        self,
        files: list[tuple[str, bytes]],
    ) -> bytes:
        if not files:
            raise ValueError("No files were provided.")
        return zip_adapter.create_archive(files)

    def find_duplicates(
        self,
        files: list[tuple[str, bytes]],
    ) -> list[dict]:
        buckets: dict[str, list[tuple[str, bytes]]] = {}
        for filename, file_data in files:
            digest = sha256_hex(file_data)
            buckets.setdefault(digest, []).append(
                (filename, file_data)
            )
        return [
            {
                "hash": digest,
                "filenames": [
                    name for name, _ in group
                ],
                "size_bytes": len(group[0][1]),
            }
            for digest, group in buckets.items()
            if len(group) > 1
        ]


file_tools_service = FileToolsService()
