import logging
from pathlib import Path

from app.core.config import settings


class LocalStorage:
    def __init__(self) -> None:
        self.upload_path = settings.upload_path
        self.processed_path = settings.processed_path
        self.compressed_path = settings.compressed_path
        self.temp_path = settings.temp_path
        self._initialize_directories()

    def _initialize_directories(self) -> None:
        directories = (
            self.upload_path,
            self.processed_path,
            self.compressed_path,
            self.temp_path,
        )
        for directory in directories:
            try:
                directory.mkdir(
                    parents=True,
                    exist_ok=True,
                )
            except OSError:
                logging.getLogger(__name__).warning(
                    "Could not create directory %s (filesystem not writable)",
                    directory,
                )

    def save(
        self,
        source_path: Path,
        destination_path: Path,
    ) -> Path:
        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        source_path.replace(destination_path)
        return destination_path

    def delete(self, file_path: Path) -> None:
        if file_path.exists():
            file_path.unlink()

    def exists(self, file_path: Path) -> bool:
        return file_path.exists()

    def get_size(self, file_path: Path) -> int:
        return file_path.stat().st_size


storage = LocalStorage()