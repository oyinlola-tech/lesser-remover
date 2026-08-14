import json
import logging
import tempfile
from pathlib import Path

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)

BLOB_BASE_URL = "https://blob.vercel-storage.com"

_LOCAL_ROOT = Path(tempfile.gettempdir()) / "vercel_storage"


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
        self.upload_path = _LOCAL_ROOT / "uploads"
        self.processed_path = _LOCAL_ROOT / "processed"
        self.compressed_path = _LOCAL_ROOT / "compressed"
        self.temp_path = _LOCAL_ROOT / "temp"
        for directory in (
            self.upload_path,
            self.processed_path,
            self.compressed_path,
            self.temp_path,
        ):
            directory.mkdir(parents=True, exist_ok=True)

    def _blob_key(self, file_path: Path) -> str:
        try:
            return file_path.relative_to(_LOCAL_ROOT).as_posix()
        except ValueError:
            return file_path.as_posix()

    def _put_blob(self, file_path: Path, data: bytes) -> None:
        blob_path = self._blob_key(file_path)
        response = requests.put(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
            data=data,
        )
        response.raise_for_status()

    def write(self, file_path: Path, data: bytes) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)
        self._put_blob(file_path, data)

    def save(
        self,
        source_path: Path,
        destination_path: Path,
    ) -> Path:
        data = source_path.read_bytes()
        self.write(destination_path, data)
        return destination_path

    def read(self, file_path: Path) -> bytes:
        blob_path = self._blob_key(file_path)
        response = requests.get(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
        )
        response.raise_for_status()
        return response.content

    def materialize(self, file_path: Path) -> Path:
        if file_path.exists():
            return file_path
        try:
            data = self.read(file_path)
        except requests.HTTPError as error:
            if error.response is not None and error.response.status_code == 404:
                return file_path
            raise
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)
        return file_path

    def delete(self, file_path: Path) -> None:
        blob_path = self._blob_key(file_path)
        response = requests.delete(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
        )
        if response.status_code == 404:
            return
        response.raise_for_status()
        file_path.unlink(missing_ok=True)

    def exists(self, file_path: Path) -> bool:
        blob_path = self._blob_key(file_path)
        response = requests.head(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
        )
        return response.status_code == 200

    def get_size(self, file_path: Path) -> int:
        blob_path = self._blob_key(file_path)
        response = requests.head(
            f"{BLOB_BASE_URL}/{blob_path}",
            headers=self._headers,
        )
        response.raise_for_status()
        return int(response.headers.get("Content-Length", 0))

    def get_url(self, file_path: Path) -> str:
        return f"{BLOB_BASE_URL}/{self._blob_key(file_path)}"


vercel_storage = VercelStorage()