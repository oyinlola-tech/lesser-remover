"""Content hashing helpers."""

import hashlib
from pathlib import Path


def sha256_hex(data: bytes) -> str:
    """SHA-256 digest of in-memory bytes as a hex string."""
    return hashlib.sha256(data).hexdigest()


def sha256_hex_file(file_path: Path) -> str:
    """SHA-256 digest of a file, streamed to keep memory bounded."""
    digest = hashlib.sha256()
    with file_path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_hex_file_like(data: bytes) -> str:
    return sha256_hex(data)
