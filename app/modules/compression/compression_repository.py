from pathlib import Path

from app.infrastructure.jobs.local_job_storage import (
    local_job_storage,
)
from app.infrastructure.storage.local_storage import storage
from app.shared.utils.file_util import resolve_safe_path


class CompressionRepository:
    def save(
        self,
        data: bytes,
        filename: str,
    ) -> Path:
        output_path = resolve_safe_path(
            storage.compressed_path,
            filename,
        )
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        output_path.write_bytes(data)
        return output_path

    def get(
        self,
        filename: str,
    ) -> Path:
        return resolve_safe_path(
            storage.compressed_path,
            filename,
        )

    def save_download(
        self,
        data: bytes,
        filename: str,
    ) -> Path:
        return local_job_storage.save_download(
            filename,
            data,
        )


compression_repository = CompressionRepository()
