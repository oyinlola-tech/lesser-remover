"""Vercel Blob-backed job storage.

Job metadata, inputs, outputs and downloads live in Vercel Blob through
the official ``vercel`` Python SDK. Paths mirror the local layout
(``jobs/{job_id}/...``, ``downloads/...``) so the drivers are
interchangeable, with a local temp mirror for fast in-instance access.
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.infrastructure.jobs.vercel_files import (
    delete_job,
    materialize_download,
    move_download,
    save_download,
    save_file,
)
from app.infrastructure.jobs.vercel_metadata import (
    read_metadata,
    write_metadata,
)

_LOCAL_ROOT = Path(tempfile.gettempdir()) / "vercel_jobs"


class VercelJobStorage:

    def __init__(self) -> None:
        if not settings.blob_read_write_token:
            raise ValueError(
                "BLOB_READ_WRITE_TOKEN is required for Vercel job storage."
            )
        self._access = settings.blob_access_mode
        self._prefix = "jobs"
        self.root_path = _LOCAL_ROOT / self._prefix
        self.download_path = _LOCAL_ROOT / "downloads"
        self.root_path.mkdir(parents=True, exist_ok=True)
        self.download_path.mkdir(parents=True, exist_ok=True)

    def create_job(self) -> str:
        job_id = uuid4().hex
        (self.get_job_path(job_id) / "input").mkdir(parents=True, exist_ok=True)
        (self.get_job_path(job_id) / "output").mkdir(parents=True, exist_ok=True)
        metadata = {
            "job_id": job_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "created",
        }
        self.write_metadata(job_id, metadata)
        return job_id

    def get_job_path(self, job_id: str) -> Path:
        return self.root_path / job_id

    def get_input_path(self, job_id: str) -> Path:
        return self.get_job_path(job_id) / "input"

    def get_output_path(self, job_id: str) -> Path:
        return self.get_job_path(job_id) / "output"

    def get_metadata_path(self, job_id: str) -> Path:
        return self.get_job_path(job_id) / "metadata.json"

    def write_metadata(
        self,
        job_id: str,
        metadata: dict,
    ) -> None:
        write_metadata(self._prefix, self._access, job_id, metadata)

    def read_metadata(self, job_id: str) -> dict:
        return read_metadata(self._prefix, self._access, job_id)

    def save_input(
        self,
        job_id: str,
        filename: str,
        data: bytes,
    ) -> Path:
        return save_file(
            self._prefix,
            self._access,
            job_id,
            filename,
            data,
            "input",
            self.root_path,
        )

    def save_output(
        self,
        job_id: str,
        filename: str,
        data: bytes,
    ) -> Path:
        return save_file(
            self._prefix,
            self._access,
            job_id,
            filename,
            data,
            "output",
            self.root_path,
        )

    def save_download(
        self,
        filename: str,
        data: bytes,
    ) -> Path:
        return save_download(
            self._prefix,
            self._access,
            filename,
            data,
            self.download_path,
        )

    def materialize_download(
        self,
        filename: str,
    ) -> Path:
        return materialize_download(
            self._prefix,
            self._access,
            filename,
            self.download_path,
        )

    def move_download(
        self,
        source_path: Path,
        filename: str,
    ) -> Path:
        return move_download(
            self._prefix,
            self._access,
            source_path,
            filename,
            self.download_path,
        )

    def delete_job(self, job_id: str) -> None:
        delete_job(self._prefix, job_id, self.root_path)
