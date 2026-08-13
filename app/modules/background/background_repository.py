from pathlib import Path

from app.infrastructure.storage.local_storage import storage
from app.shared.utils.file_util import resolve_safe_path


class BackgroundRepository:
    def save_processed_file(
        self,
        data: bytes,
        filename: str,
    ) -> Path:
        output_path = resolve_safe_path(
            storage.processed_path,
            filename,
        )
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        output_path.write_bytes(data)
        return output_path

    def get_processed_file(
        self,
        filename: str,
    ) -> Path:
        return resolve_safe_path(
            storage.processed_path,
            filename,
        )

    def get_file_size(
        self,
        file_path: Path,
    ) -> int:
        return storage.get_size(file_path)


background_repository = BackgroundRepository()