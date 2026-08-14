"""Unit tests for the file tools service (Phase 7)."""

from io import BytesIO

from PIL import Image

from app.modules.file_tools.file_tool_service import (
    file_tools_service,
)


def _png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGBA", (30, 20), (1, 2, 3, 255)).save(
        buffer,
        format="PNG",
    )
    return buffer.getvalue()


def test_analyze_reports_image_details():
    results = file_tools_service.analyze(
        [("photo.png", _png_bytes())]
    )
    item = results[0]
    assert item["category"] == "image"
    assert item["width"] == 30
    assert item["height"] == 20
    assert len(item["sha256"]) == 64


def test_analyze_handles_unknown_files():
    results = file_tools_service.analyze(
        [("notes.txt", b"hello world")]
    )
    assert results[0]["category"] == "unknown"
    assert results[0]["mime_type"] == "application/octet-stream"


def test_create_zip_packages_files():
    data = file_tools_service.create_zip(
        [
            ("a.png", _png_bytes()),
            ("b.png", _png_bytes()),
        ]
    )
    assert data[:2] == b"PK"


def test_create_zip_requires_files():
    try:
        file_tools_service.create_zip([])
    except ValueError as error:
        assert "No files" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_find_duplicates_groups_identical_files():
    groups = file_tools_service.find_duplicates(
        [
            ("one.png", _png_bytes()),
            ("copy.png", _png_bytes()),
            ("unique.png", b"something else"),
        ]
    )
    assert len(groups) == 1
    assert set(groups[0]["filenames"]) == {"one.png", "copy.png"}
    assert groups[0]["size_bytes"] == len(_png_bytes())


def test_find_duplicates_returns_empty_when_unique():
    groups = file_tools_service.find_duplicates(
        [
            ("a.png", b"aaa"),
            ("b.png", b"bbb"),
        ]
    )
    assert groups == []
