"""Unit tests for the developer tools service (Phase 8)."""

from io import BytesIO

from PIL import Image

from app.modules.devtools.dev_tools_service import dev_tools_service


def _png_bytes(size=64) -> bytes:
    buffer = BytesIO()
    Image.new("RGBA", (size, size), (22, 51, 0, 255)).save(
        buffer,
        format="PNG",
    )
    return buffer.getvalue()


def test_generate_favicon_returns_ico_and_png():
    result = dev_tools_service.generate_favicon(_png_bytes(), size=64)
    assert result["ico"]
    assert result["png"]
    assert 16 in result["sizes"]
    assert 32 in result["sizes"]


def test_generate_favicon_pads_non_square():
    buffer = BytesIO()
    Image.new("RGB", (80, 40), (1, 2, 3)).save(buffer, format="PNG")
    result = dev_tools_service.generate_favicon(buffer.getvalue(), size=48)
    assert result["png"]


def test_optimize_svg_strips_comments_and_shrinks():
    svg = b'<svg xmlns="http://www.w3.org/2000/svg"><!-- drop --><path d="M 0 0 L 1 1" /></svg>'
    result = dev_tools_service.optimize_svg(svg, precision=2)
    assert result["minified_size"] < result["original_size"]
    assert b"drop" not in result["data"]
    assert b"1" in result["data"]


def test_optimize_svg_rounds_numbers():
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="100.456" height="50"><rect width="100.456" height="50" /></svg>'
    result = dev_tools_service.optimize_svg(svg, precision=1)
    assert b"100.5" in result["data"]
    assert b"100.456" not in result["data"]


def test_optimize_svg_rejects_invalid_xml():
    try:
        dev_tools_service.optimize_svg(b"<svg><unclosed>")
    except ValueError as error:
        assert "Invalid SVG" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_generate_qr_png():
    data, content_type = dev_tools_service.generate_qr(
        "https://example.com"
    )
    assert content_type == "image/png"
    assert data[:8] == b"\x89PNG\r\n\x1a\n"


def test_generate_qr_svg():
    data, content_type = dev_tools_service.generate_qr(
        "https://example.com",
        output_format="svg",
    )
    assert content_type == "image/svg+xml"
    assert b"<svg" in data


def test_generate_qr_with_logo():
    data, content_type = dev_tools_service.generate_qr(
        "https://example.com",
        image_data=_png_bytes(16),
    )
    assert content_type == "image/png"


def test_generate_qr_rejects_empty_content():
    try:
        dev_tools_service.generate_qr("   ")
    except ValueError as error:
        assert "cannot be empty" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_generate_barcode_png():
    data, content_type = dev_tools_service.generate_barcode(
        "HELLO-123",
        code_type="code128",
    )
    assert content_type == "image/png"


def test_generate_barcode_svg():
    data, content_type = dev_tools_service.generate_barcode(
        "5901234123457",
        code_type="ean13",
        output_format="svg",
    )
    assert content_type == "image/svg+xml"
    assert b"<svg" in data


def test_generate_barcode_rejects_unknown_type():
    try:
        dev_tools_service.generate_barcode("123", code_type="nope")
    except ValueError as error:
        assert "Unsupported" in str(error)
    else:
        raise AssertionError("Expected ValueError")
