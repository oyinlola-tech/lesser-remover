"""Vercel Blob file operations with local temp mirrors."""

import logging
import shutil
from pathlib import Path

from app.infrastructure.jobs.vercel_blob_io import (
    blob_path,
    get_blob,
    put_blob,
)

logger = logging.getLogger(__name__)


def save_file(
    prefix: str,
    access: str,
    job_id: str,
    filename: str,
    data: bytes,
    folder: str,
    local_root: Path,
) -> Path:
    path = blob_path(prefix, job_id, f"{folder}/{filename}")
    put_blob(path, data, access)
    local_path = local_root / job_id / folder / filename
    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)
    except OSError:
        logger.debug(
            "Local mirror write failed for %s; blob is source of truth.",
            path,
        )
    return local_path


def save_download(
    prefix: str,
    access: str,
    filename: str,
    data: bytes,
    download_path: Path,
) -> Path:
    path = f"downloads/{filename}"
    put_blob(path, data, access)
    local_path = download_path / filename
    try:
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(data)
    except OSError:
        logger.debug(
            "Local mirror write failed for download %s; blob is source of truth.",
            path,
        )
    return local_path


def materialize_download(
    prefix: str,
    access: str,
    filename: str,
    download_path: Path,
) -> Path:
    path = download_path / filename
    if path.exists():
        return path
    data = get_blob(f"downloads/{filename}", access)
    if data is None:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def move_download(
    prefix: str,
    access: str,
    source_path: Path,
    filename: str,
    download_path: Path,
) -> Path:
    data = source_path.read_bytes() if source_path.exists() else b""
    return save_download(prefix, access, filename, data, download_path)


def delete_job(prefix: str, job_id: str, local_root: Path) -> None:
    from app.infrastructure.jobs.vercel_blob_io import (
        delete_blob_prefix,
    )

    delete_blob_prefix(prefix, job_id)
    shutil.rmtree(local_root / job_id, ignore_errors=True)
