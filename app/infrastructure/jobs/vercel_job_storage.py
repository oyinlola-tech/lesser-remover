import json
import logging
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)

BLOB_BASE_URL = "https://blob.vercel-storage.com"

_LOCAL_ROOT = Path(tempfile.gettempdir()) / "vercel_jobs"


class VercelJobStorage:
    def __init__(self) -> None:
        self._token = settings.blob_read_write_token
        if not self._token:
            raise ValueError(
                "BLOB_READ_WRITE_TOKEN is required for Vercel job storage."
            )
        self._headers = {
            "Authorization": f"Bearer {self._token}",
        }
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
        response = requests.put(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
            data=data,
        )
        response.raise_for_status()

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
        response = requests.get(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
        )
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        return response.json()

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
        response = requests.get(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
        )
        if response.status_code == 404:
            return path
        response.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
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
        response = requests.get(
            f"{BLOB_BASE_URL}/list",
            headers=self._headers,
            params={"prefix": prefix},
        )
        response.raise_for_status()
        blobs = response.json().get("blobs", [])
        for blob in blobs:
            delete_response = requests.delete(
                f"{BLOB_BASE_URL}/{blob['pathname']}",
                headers=self._headers,
            )
            delete_response.raise_for_status()
        shutil.rmtree(self.get_job_path(job_id), ignore_errors=True)


vercel_job_storage = VercelJobStorage()