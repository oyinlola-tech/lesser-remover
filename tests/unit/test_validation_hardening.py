"""Tests for hashing and upload validation hardening."""

import pytest
from fastapi import HTTPException

from app.shared.constants.file_constants import (
    MAX_FILES_PER_BATCH,
)
from app.shared.file_inspection.file_validation import (
    extension_matches_mime,
    validate_file_count,
    validate_filename_extension,
)
from app.shared.utils.hash_util import (
    sha256_hex,
    sha256_hex_file,
)


def test_sha256_hex_known_vector():
    assert sha256_hex(b"") == (
        "e3b0c44298fc1c149afbf4c8996fb924"
        "27ae41e4649b934ca495991b7852b855"
    )
    assert sha256_hex(b"abc") == (
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )


def test_sha256_hex_file_matches_bytes(tmp_path):
    path = tmp_path / "sample.bin"
    data = b"hello file hashing" * 100
    path.write_bytes(data)
    assert sha256_hex_file(path) == sha256_hex(data)


def test_sha256_hex_file_streams_large_data(tmp_path):
    path = tmp_path / "large.bin"
    path.write_bytes(b"x" * (3 * 1024 * 1024))
    assert sha256_hex_file(path) == sha256_hex(b"x" * (3 * 1024 * 1024))


def test_extension_matches_mime():
    assert extension_matches_mime("photo.jpg", "image/jpeg")
    assert extension_matches_mime("photo.jpeg", "image/jpeg")
    assert extension_matches_mime("photo.png", "image/png")
    assert extension_matches_mime("photo.webp", "image/webp")
    assert extension_matches_mime("doc.pdf", "application/pdf")
    assert not extension_matches_mime("photo.txt", "image/png")
    assert not extension_matches_mime("photo.png", "application/pdf")


def test_validate_filename_extension_rejects_mismatch():
    with pytest.raises(HTTPException):
        validate_filename_extension("photo.txt", "image/png")


def test_validate_filename_extension_accepts_match():
    validate_filename_extension("photo.jpg", "image/jpeg")


def test_validate_file_count_rejects_zero():
    with pytest.raises(HTTPException):
        validate_file_count(0)


def test_validate_file_count_rejects_above_limit():
    with pytest.raises(HTTPException):
        validate_file_count(MAX_FILES_PER_BATCH + 1)


def test_validate_file_count_accepts_at_limit():
    validate_file_count(MAX_FILES_PER_BATCH)
    validate_file_count(1)
