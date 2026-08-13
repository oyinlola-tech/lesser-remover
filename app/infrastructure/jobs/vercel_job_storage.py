import json
from pathlib import Path
from uuid import uuid4

import requests

from app.core.config import settings

BLOB_BASE_URL = "https://blob.vercel-storage.com"


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

    def _job_prefix(self, job_id: str) -> str:
        return f"{self._prefix}/{job_id}"

    def _blob_path(self, job_id: str, filename: str) -> str:
        return f"{self._job_prefix(job_id)}/{filename}"

    def create_job(self) -> str:
        job_id = uuid4().hex
        metadata = {
            "job_id": job_id,
            "status": "created",
        }
        self.write_metadata(job_id, metadata)
        return job_id

    def get_job_path(self, job_id: str) -> Path:
        return Path(self._job_prefix(job_id))

    def get_input_path(self, job_id: str) -> Path:
        return Path(f"{self._job_prefix(job_id)}/input")

    def get_output_path(self, job_id: str) -> Path:
        return Path(f"{self._job_prefix(job_id)}/output")

    def get_metadata_path(self, job_id: str) -> Path:
        return Path(f"{self._job_prefix(job_id)}/metadata.json")

    def write_metadata(
        self,
        job_id: str,
        metadata: dict,
    ) -> None:
        blob_path = self._blob_path(job_id, "metadata.json")
        response = requests.put(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
            data=json.dumps(metadata),
        )
        response.raise_for_status()

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
        blob_path = self._blob_path(job_id, f"input/{filename}")
        response = requests.put(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
            data=data,
        )
        response.raise_for_status()
        return Path(blob_path)

    def save_output(
        self,
        job_id: str,
        filename: str,
        data: bytes,
    ) -> Path:
        blob_path = self._blob_path(job_id, f"output/{filename}")
        response = requests.put(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
            data=data,
        )
        response.raise_for_status()
        return Path(blob_path)

    def save_download(
        self,
        filename: str,
        data: bytes,
    ) -> Path:
        blob_path = f"downloads/{filename}"
        response = requests.put(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
            data=data,
        )
        response.raise_for_status()
        return Path(blob_path)

    def move_download(
        self,
        source_path: Path,
        filename: str,
    ) -> Path:
        return self.save_download(filename, b"")

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


vercel_job_storage = VercelJobStorage()
