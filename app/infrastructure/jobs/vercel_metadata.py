"""Vercel Blob metadata operations."""

import json

from app.infrastructure.jobs.vercel_blob_io import (
    blob_path,
    decode_metadata,
    get_blob,
    put_blob,
)


def write_metadata(
    prefix: str,
    access: str,
    job_id: str,
    metadata: dict,
) -> None:
    path = blob_path(prefix, job_id, "metadata.json")
    put_blob(path, json.dumps(metadata).encode("utf-8"), access)


def read_metadata(
    prefix: str,
    access: str,
    job_id: str,
) -> dict:
    path = blob_path(prefix, job_id, "metadata.json")
    return decode_metadata(get_blob(path, access))
