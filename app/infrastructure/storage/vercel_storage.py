import json
from pathlib import Path

import requests

from app.core.config import settings

BLOB_BASE_URL = "https://blob.vercel-storage.com"


class VercelStorage:
    def __init__(self) -> None:
        self._token = settings.blob_read_write_token
        if not self._token:
            raise ValueError(
                "BLOB_READ_WRITE_TOKEN is required for Vercel storage."
            )
        self._headers = {
            "Authorization": f"Bearer {self._token}",
        }

    def _blob_path(self, file_path: Path) -> str:
        return file_path.as_posix()

    def save(
        self,
        source_path: Path,
        destination_path: Path,
    ) -> Path:
        data = source_path.read_bytes()
        blob_path = self._blob_path(destination_path)
        response = requests.put(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
            data=data,
        )
        response.raise_for_status()
        return destination_path

    def delete(self, file_path: Path) -> None:
        blob_path = self._blob_path(file_path)
        response = requests.delete(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
        )
        if response.status_code == 404:
            return
        response.raise_for_status()

    def exists(self, file_path: Path) -> bool:
        blob_path = self._blob_path(file_path)
        response = requests.head(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
        )
        return response.status_code == 200

    def get_size(self, file_path: Path) -> int:
        blob_path = self._blob_path(file_path)
        response = requests.head(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
        )
        response.raise_for_status()
        return int(response.headers.get("Content-Length", 0))

    def read(self, file_path: Path) -> bytes:
        blob_path = self._blob_path(file_path)
        response = requests.get(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
        )
        response.raise_for_status()
        return response.content

    def get_url(self, file_path: Path) -> str:
        blob_path = self._blob_path(file_path)
        return f"{BLOB_BASE_URL}/{blob_path}"


vercel_storage = VercelStorage()
