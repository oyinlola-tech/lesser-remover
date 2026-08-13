from pathlib import Path

from app.infrastructure.archive.zip_adapter import (
    zip_adapter,
)


class ArchiveService:
    def create_zip(
        self,
        files: list[tuple[str, bytes]],
    ) -> bytes:
        if not files:
            raise ValueError(
                "Cannot create an empty archive."
            )
        return zip_adapter.create_archive(files)

    def create_zip_from_directory(
        self,
        source_directory: Path,
        output_path: Path,
    ) -> Path:
        return zip_adapter.create_archive_from_directory(
            source_directory,
            output_path,
        )


archive_service = ArchiveService()
