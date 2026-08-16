"""Vercel Blob-backed job storage.

Job metadata, inputs, outputs and downloads live in Vercel Blob through
the official ``vercel`` Python SDK. Paths mirror the local layout
(``jobs/{job_id}/...``, ``downloads/...``) so the drivers are
interchangeable, with a local temp mirror for fast in-instance access.
"""

import json
import logging
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from vercel.blob import (
    BlobNotFoundError,
    delete,
    get,
    list_objects,
    put,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

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

    def _job_prefix(self, job_id: str) -> str:
        return f"{self._prefix}/{job_id}"

    def _blob_path(self, job_id: str, filename: str) -> str:
        return f"{self._job_prefix(job_id)}/{filename}"

    def _put_blob(self, blob_path: str, data: bytes) -> None:
        put(blob_path, data, access=self._access)

    def create_job(self) -> str:
        job_id = uuid4().hex
        job_path = self.get_job_path(job_id)
        (job_path / "input").mkdir(parents=True, exist_ok=True)
        (job_path / "output").mkdir(parents=True, exist_ok=True)
        metadata = {
            "job_id": job_id,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
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
        blob_path = self._blob_path(job_id, "metadata.json")
        self._put_blob(
            blob_path,
            json.dumps(metadata).encode("utf-8"),
        )

    def read_metadata(self, job_id: str) -> dict:
        blob_path = self._blob_path(job_id, "metadata.json")
        try:
            result = get(blob_path, access=self._access)
        except BlobNotFoundError:
            return {}
        return json.loads(result.content.decode("utf-8"))

    def save_input(
        self,
        job_id: str,
        filename: str,
        data: bytes,
    ) -> Path:
        path = self.get_input_path(job_id) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self._put_blob(
            self._blob_path(job_id, f"input/{filename}"),
            data,
        )
        return path

    def save_output(
        self,
        job_id: str,
        filename: str,
        data: bytes,
    ) -> Path:
        path = self.get_output_path(job_id) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self._put_blob(
            self._blob_path(job_id, f"output/{filename}"),
            data,
        )
        return path

    def save_download(
        self,
        filename: str,
        data: bytes,
    ) -> Path:
        path = self.download_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self._put_blob(
            f"downloads/{filename}",
            data,
        )
        return path

    def materialize_download(
        self,
        filename: str,
    ) -> Path:
        path = self.download_path / filename
        if path.exists():
            return path
        blob_path = f"downloads/{filename}"
        try:
            result = get(blob_path, access=self._access)
        except BlobNotFoundError:
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(result.content)
        return path

    def move_download(
        self,
        source_path: Path,
        filename: str,
    ) -> Path:
        data = (
            source_path.read_bytes()
            if source_path.exists()
            else b""
        )
        return self.save_download(filename, data)

    def delete_job(self, job_id: str) -> None:
        prefix = self._job_prefix(job_id)
        blobs = []
        cursor = None
        while True:
            page = list_objects(
                prefix=prefix,
                cursor=cursor,
                limit=1000,
            )
            blobs.extend(page.blobs)
            if not page.has_more or page.cursor is None:
                break
            cursor = page.cursor
        if blobs:
            delete([blob.pathname for blob in blobs])
        shutil.rmtree(self.get_job_path(job_id), ignore_errors=True)


try:
    vercel_job_storage = VercelJobStorage()
except ValueError:
    # No token configured (e.g. local development). ``app.main`` performs
    # its own startup check with a clear message when STORAGE_DRIVER=vercel,
    # so a missing token here just leaves the singleton unset.
    vercel_job_storage = None  # type: ignore[assignment]
