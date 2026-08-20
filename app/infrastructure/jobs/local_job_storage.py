"""Local filesystem job storage."""

from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.infrastructure.jobs.local_files import (
    delete_job,
    materialize_download,
    move_download,
    save_download,
    save_input,
    save_output,
)
from app.infrastructure.jobs.local_metadata import (
    create_job_metadata,
    read_metadata,
    write_metadata,
)
from app.infrastructure.jobs.local_paths import (
    get_input_path,
    get_job_path,
    get_metadata_path,
    get_output_path,
    prepare_directories,
)


class LocalJobStorage:

    def __init__(self) -> None:
        self.root_path = settings.job_path
        self.download_path = settings.download_path
        prepare_directories(self.root_path, self.download_path)

    def create_job(self) -> str:
        job_id = uuid4().hex
        input_path = get_input_path(self.root_path, job_id)
        output_path = get_output_path(self.root_path, job_id)
        input_path.mkdir(parents=True, exist_ok=True)
        output_path.mkdir(parents=True, exist_ok=True)
        job_id, _ = create_job_metadata(self.root_path, job_id)
        return job_id

    def get_job_path(self, job_id: str) -> Path:
        return get_job_path(self.root_path, job_id)

    def get_input_path(self, job_id: str) -> Path:
        return get_input_path(self.root_path, job_id)

    def get_output_path(self, job_id: str) -> Path:
        return get_output_path(self.root_path, job_id)

    def get_metadata_path(self, job_id: str) -> Path:
        return get_metadata_path(self.root_path, job_id)

    def write_metadata(
        self,
        job_id: str,
        metadata: dict,
    ) -> None:
        write_metadata(self.root_path, job_id, metadata)

    def read_metadata(self, job_id: str) -> dict:
        return read_metadata(self.root_path, job_id)

    def save_input(
        self,
        job_id: str,
        filename: str,
        data: bytes,
    ) -> Path:
        return save_input(
            self.root_path,
            job_id,
            filename,
            data,
        )

    def save_output(
        self,
        job_id: str,
        filename: str,
        data: bytes,
    ) -> Path:
        return save_output(
            self.root_path,
            job_id,
            filename,
            data,
        )

    def save_download(
        self,
        filename: str,
        data: bytes,
    ) -> Path:
        return save_download(self.download_path, filename, data)

    def materialize_download(
        self,
        filename: str,
    ) -> Path:
        return materialize_download(self.download_path, filename)

    def move_download(
        self,
        source_path: Path,
        filename: str,
    ) -> Path:
        return move_download(
            self.download_path,
            source_path,
            filename,
        )

    def delete_job(self, job_id: str) -> None:
        delete_job(self.root_path, job_id)


local_job_storage = LocalJobStorage()
