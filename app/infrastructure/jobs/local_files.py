"""Local job file persistence."""

import shutil
from pathlib import Path

from app.infrastructure.jobs.local_paths import (
    get_input_path,
    get_job_path,
    get_output_path,
)
from app.shared.utils.file_util import is_safe_filename


def save_input(
    root_path: Path,
    job_id: str,
    filename: str,
    data: bytes,
) -> Path:
    if not is_safe_filename(filename):
        raise ValueError("Invalid filename")
    path = get_input_path(root_path, job_id) / filename
    path.write_bytes(data)
    return path


def save_output(
    root_path: Path,
    job_id: str,
    filename: str,
    data: bytes,
) -> Path:
    if not is_safe_filename(filename):
        raise ValueError("Invalid filename")
    path = get_output_path(root_path, job_id) / filename
    path.write_bytes(data)
    return path


def save_download(
    download_path: Path,
    filename: str,
    data: bytes,
) -> Path:
    if not is_safe_filename(filename):
        raise ValueError("Invalid filename")
    path = download_path / filename
    path.write_bytes(data)
    return path


def materialize_download(
    download_path: Path,
    filename: str,
) -> Path:
    if not is_safe_filename(filename):
        raise ValueError("Invalid filename")
    return download_path / filename


def move_download(
    download_path: Path,
    source_path: Path,
    filename: str,
) -> Path:
    if not is_safe_filename(filename):
        raise ValueError("Invalid filename")
    destination = download_path / filename
    source_path.replace(destination)
    return destination


def delete_job(
    root_path: Path,
    job_id: str,
) -> None:
    job_path = get_job_path(root_path, job_id)
    if job_path.exists():
        shutil.rmtree(job_path)
