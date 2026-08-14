"""Tests for the local storage adapter.

These tests never touch the project's real storage directories;
all operations happen inside pytest's temporary directories.
"""

from pathlib import Path

from app.infrastructure.storage.local_storage import LocalStorage


def make_storage(tmp_path: Path) -> LocalStorage:
    storage = LocalStorage()
    storage.upload_path = tmp_path / "uploads"
    storage.processed_path = tmp_path / "processed"
    storage.compressed_path = tmp_path / "compressed"
    storage.temp_path = tmp_path / "temp"
    return storage


def test_write_and_read_roundtrip(tmp_path):
    storage = make_storage(tmp_path)
    target = tmp_path / "out" / "file.bin"
    storage.write(target, b"hello world")
    assert target.read_bytes() == b"hello world"


def test_write_creates_parent_directories(tmp_path):
    storage = make_storage(tmp_path)
    target = tmp_path / "deep" / "nested" / "file.txt"
    storage.write(target, b"data")
    assert target.is_file()


def test_save_moves_source_to_destination(tmp_path):
    storage = make_storage(tmp_path)
    source = tmp_path / "source.bin"
    source.write_bytes(b"payload")
    destination = tmp_path / "moved" / "destination.bin"
    result = storage.save(source, destination)
    assert result == destination
    assert destination.read_bytes() == b"payload"
    assert not source.exists()


def test_materialize_returns_same_path_locally(tmp_path):
    storage = make_storage(tmp_path)
    target = tmp_path / "file.bin"
    target.write_bytes(b"x")
    assert storage.materialize(target) == target


def test_delete_removes_file(tmp_path):
    storage = make_storage(tmp_path)
    target = tmp_path / "file.bin"
    target.write_bytes(b"x")
    storage.delete(target)
    assert not target.exists()


def test_delete_is_idempotent(tmp_path):
    storage = make_storage(tmp_path)
    storage.delete(tmp_path / "missing.bin")


def test_exists(tmp_path):
    storage = make_storage(tmp_path)
    target = tmp_path / "file.bin"
    assert not storage.exists(target)
    target.write_bytes(b"x")
    assert storage.exists(target)


def test_get_size(tmp_path):
    storage = make_storage(tmp_path)
    target = tmp_path / "file.bin"
    target.write_bytes(b"12345")
    assert storage.get_size(target) == 5
