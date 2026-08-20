"""Local job path helpers."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def prepare_directories(
    root_path: Path,
    download_path: Path,
) -> None:
    try:
        root_path.mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.warning(
            "Could not create job directory %s (filesystem not writable)",
            root_path,
        )
    try:
        download_path.mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.warning(
            "Could not create download directory %s (filesystem not writable)",
            download_path,
        )


def get_job_path(root_path: Path, job_id: str) -> Path:
    return root_path / job_id


def get_input_path(root_path: Path, job_id: str) -> Path:
    return get_job_path(root_path, job_id) / "input"


def get_output_path(root_path: Path, job_id: str) -> Path:
    return get_job_path(root_path, job_id) / "output"


def get_metadata_path(root_path: Path, job_id: str) -> Path:
    return get_job_path(root_path, job_id) / "metadata.json"
