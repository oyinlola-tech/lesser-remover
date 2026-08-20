import logging
import time
from io import BytesIO

from PIL import Image

from app.core.logging import get_tool_logger
from app.infrastructure.archive.zip_adapter import zip_adapter
from app.shared.file_inspection.file_inspector import (
    file_inspector,
)
from app.shared.utils.hash_util import sha256_hex

logger = logging.getLogger(__name__)


class FileToolsService:
    def analyze(
        self,
        files: list[tuple[str, bytes]],
    ) -> list[dict]:
        tool_logger = get_tool_logger("file-analyzer")
        started = time.monotonic()
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
                except Exception as error:
                    logger.debug(
                        "Failed to read PDF metadata for %s: %s",
                        filename,
                        error,
                    )
            results.append(result)
        tool_logger.info(
            "analyzed %d files (%d bytes total) in %.2fs",
            len(files),
            sum(len(data) for _, data in files),
            time.monotonic() - started,
        )
        return results

    def create_zip(
        self,
        files: list[tuple[str, bytes]],
    ) -> bytes:
        tool_logger = get_tool_logger("zip-creator")
        started = time.monotonic()
        if not files:
            raise ValueError("No files were provided.")
        archive = zip_adapter.create_archive(files)
        tool_logger.info(
            "created zip with %d files (%d bytes) in %.2fs",
            len(files),
            len(archive),
            time.monotonic() - started,
        )
        return archive

    def find_duplicates(
        self,
        files: list[tuple[str, bytes]],
    ) -> list[dict]:
        tool_logger = get_tool_logger("duplicate-finder")
        started = time.monotonic()
        buckets: dict[str, list[tuple[str, bytes]]] = {}
        for filename, file_data in files:
            digest = sha256_hex(file_data)
            buckets.setdefault(digest, []).append(
                (filename, file_data)
            )
        duplicates = [
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
        tool_logger.info(
            "checked %d files, found %d duplicate groups in %.2fs",
            len(files),
            len(duplicates),
            time.monotonic() - started,
        )
        return duplicates


file_tools_service = FileToolsService()
