from pathlib import Path

from app.infrastructure.storage import storage
from app.shared.utils.file_util import resolve_safe_path


class FileToolRepository:
    def save_output_file(
        self,
        data: bytes,
        filename: str,
    ) -> Path:
        output_path = resolve_safe_path(
            storage.processed_path,
            filename,
        )
        storage.write(output_path, data)
        return output_path

    def get_output_file(
        self,
        filename: str,
    ) -> Path:
        return storage.materialize(
            resolve_safe_path(
                storage.processed_path,
                filename,
            )
        )


file_tool_repository = FileToolRepository()
