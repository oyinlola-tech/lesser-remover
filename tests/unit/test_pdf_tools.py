"""Unit tests for the PDF tools service (Phase 6)."""

from io import BytesIO

from PIL import Image

from app.modules.pdf.pdf_service import (
    _parse_page_selection,
    pdf_service,
)


def _pdf_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (200, 100), (255, 255, 255)).save(
        buffer,
        format="PDF",
    )
    return buffer.getvalue()


def test_merge_combines_pages():
    data, page_count = pdf_service.merge(
        [
            ("a.pdf", _pdf_bytes()),
            ("b.pdf", _pdf_bytes()),
        ]
    )
    assert page_count == 2
    assert data[:4] == b"%PDF"


def test_merge_requires_two_files():
    try:
        pdf_service.merge([("a.pdf", _pdf_bytes())])
    except ValueError as error:
        assert "two" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_split_returns_zip_of_pages():
    data, entries = pdf_service.split(_pdf_bytes(), "document.pdf")
    assert len(entries) == 1
    assert entries[0].startswith("document-page-1.pdf")
    assert data[:2] == b"PK"


def test_rotate_single_page():
    data, page_count = pdf_service.rotate(_pdf_bytes(), 90)
    assert page_count == 1
    assert data[:4] == b"%PDF"


def test_rotate_rejects_bad_angle():
    try:
        pdf_service.rotate(_pdf_bytes(), 45)
    except ValueError as error:
        assert "90" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_extract_pages():
    data, entries = pdf_service.extract_pages(
        _pdf_bytes(),
        "1",
        "document.pdf",
    )
    assert len(entries) == 1
    assert data[:2] == b"PK"


def test_extract_pages_out_of_range():
    try:
        pdf_service.extract_pages(_pdf_bytes(), "5", "document.pdf")
    except ValueError as error:
        assert "Invalid page" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_from_images_creates_pdf():
    images = [
        ("one.png", _image_bytes()),
        ("two.png", _image_bytes()),
    ]
    data, page_count = pdf_service.from_images(images)
    assert page_count == 2
    assert data[:4] == b"%PDF"


def test_page_count():
    assert pdf_service.page_count(_pdf_bytes()) == 1


def test_parse_page_selection():
    assert _parse_page_selection("1,3-5", 8) == [1, 3, 4, 5]
    assert _parse_page_selection("1-3,3", 8) == [1, 2, 3]
    try:
        _parse_page_selection("9", 8)
    except ValueError as error:
        assert "Invalid page" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def _image_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (50, 50), (10, 20, 30)).save(
        buffer,
        format="PNG",
    )
    return buffer.getvalue()
