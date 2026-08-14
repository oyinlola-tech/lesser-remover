"""Tests for configuration validation and environment handling."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_defaults_are_local_first():
    settings = Settings(
        _env_file=None,
        app_name="Utils-tool",
    )
    assert settings.app_name == "Utils-tool"
    assert settings.storage_driver == "local"
    assert settings.app_env == "development"
    assert settings.job_ttl_minutes == 30
    assert settings.max_upload_size_mb == 100


def test_storage_driver_validates():
    with pytest.raises(ValidationError):
        Settings(storage_driver="s3")

    with pytest.raises(ValidationError):
        Settings(storage_driver="database")


def test_storage_driver_accepts_local_and_vercel():
    assert Settings(storage_driver="local").storage_driver == "local"
    assert Settings(storage_driver="vercel").storage_driver == "vercel"


def test_app_env_validates():
    with pytest.raises(ValidationError):
        Settings(app_env="staging")


def test_max_upload_size_bytes_property():
    settings = Settings(max_upload_size_mb=42)
    assert settings.max_upload_size_bytes == 42 * 1024 * 1024


def test_cors_origins_list_splits_and_trims():
    settings = Settings(
        cors_origins="http://127.0.0.1:8000, http://localhost:8000 ,"
    )
    assert settings.cors_origins_list == [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]


def test_directory_properties():
    settings = Settings(
        upload_directory="storage/uploads",
        processed_directory="storage/processed",
    )
    assert str(settings.upload_path) == "storage/uploads"
    assert str(settings.processed_path) == "storage/processed"
