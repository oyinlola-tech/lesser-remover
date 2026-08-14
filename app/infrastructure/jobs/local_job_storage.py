import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.shared.utils.file_util import is_safe_filename


class LocalJobStorage:
    def __init__(self) -> None:
        self.root_path = settings.job_path
        self.download_path = settings.download_path
        try:
            self.root_path.mkdir(
                parents=True,
                exist_ok=True,
            )
        except OSError:
            logging.getLogger(__name__).warning(
                "Could not create job directory %s (filesystem not writable)",
                self.root_path,
            )
        try:
            self.download_path.mkdir(
                parents=True,
                exist_ok=True,
            )
        except OSError:
            logging.getLogger(__name__).warning(
                "Could not create download directory %s (filesystem not writable)",
                self.download_path,
            )

    def create_job(self) -> str:
        job_id = uuid4().hex
        job_path = self.root_path / job_id
        input_path = job_path / "input"
        output_path = job_path / "output"
        input_path.mkdir(
            parents=True,
            exist_ok=True,
        )
        output_path.mkdir(
            parents=True,
            exist_ok=True,
        )
        metadata = {
            "job_id": job_id,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": "created",
        }
        self.write_metadata(
            job_id,
            metadata,
        )
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
        metadata_path = self.get_metadata_path(
            job_id
        )
        metadata_path.write_text(
            json.dumps(
                metadata,
                indent=2,
            ),
            encoding="utf-8",
        )

    def read_metadata(self, job_id: str) -> dict:
        metadata_path = self.get_metadata_path(
            job_id
        )
        if not metadata_path.exists():
            return {}
        return json.loads(
            metadata_path.read_text(
                encoding="utf-8"
            )
        )

    def save_input(
        self,
        job_id: str,
        filename: str,
        data: bytes,
    ) -> Path:
        if not is_safe_filename(filename):
            raise ValueError("Invalid filename")
        path = self.get_input_path(job_id) / filename
        path.write_bytes(data)
        return path

    def save_output(
        self,
        job_id: str,
        filename: str,
        data: bytes,
    ) -> Path:
        if not is_safe_filename(filename):
            raise ValueError("Invalid filename")
        path = self.get_output_path(job_id) / filename
        path.write_bytes(data)
        return path

    def save_download(
        self,
        filename: str,
        data: bytes,
    ) -> Path:
        if not is_safe_filename(filename):
            raise ValueError("Invalid filename")
        path = self.download_path / filename
        path.write_bytes(data)
        return path

    def materialize_download(
        self,
        filename: str,
    ) -> Path:
        if not is_safe_filename(filename):
            raise ValueError("Invalid filename")
        return self.download_path / filename

    def move_download(
        self,
        source_path: Path,
        filename: str,
    ) -> Path:
        if not is_safe_filename(filename):
            raise ValueError("Invalid filename")
        destination = (
            self.download_path
            / filename
        )
        source_path.replace(
            destination
        )
        return destination

    def delete_job(self, job_id: str) -> None:
        job_path = self.get_job_path(job_id)
        if job_path.exists():
            shutil.rmtree(job_path)


local_job_storage = LocalJobStorage()
