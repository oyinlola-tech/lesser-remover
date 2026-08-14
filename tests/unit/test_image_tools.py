"""Unit tests for the image tools service (Phase 4)."""

from io import BytesIO

from PIL import Image

from app.modules.background.background_service import background_service
from app.modules.image.image_service import image_service


def _png_bytes(size=(120, 80), color=(255, 0, 0, 255)) -> bytes:
    buffer = BytesIO()
    Image.new("RGBA", size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def _jpg_bytes(size=(120, 80)) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, (10, 200, 30)).save(buffer, format="JPEG")
    return buffer.getvalue()


def test_convert_png_to_jpg_flattens_transparency():
    result = image_service.convert(_png_bytes(), "jpg")
    assert result["extension"] == "jpg"
    assert result["content_type"] == "image/jpeg"
    assert result["flattened"] is True


def test_convert_to_avif():
    result = image_service.convert(_png_bytes(), "avif")
    assert result["content_type"] == "image/avif"
    assert result["flattened"] is False


def test_convert_rejects_unknown_format():
    try:
        image_service.convert(_png_bytes(), "tiff")
    except ValueError as error:
        assert "Unsupported" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_resize_by_percent_keeps_aspect():
    result = image_service.resize(_png_bytes(), percent=50)
    assert result["width"] == 60
    assert result["height"] == 40


def test_resize_to_exact_box():
    result = image_service.resize(
        _png_bytes(),
        width=100,
        height=100,
    )
    assert result["width"] == 100
    assert result["height"] == 100


def test_resize_cover_crops_to_fit():
    result = image_service.resize(
        _png_bytes((400, 100)),
        width=100,
        height=100,
        cover=True,
    )
    assert result["width"] == 100
    assert result["height"] == 100


def test_resize_max_dimension_shrinks_longer_edge():
    result = image_service.resize(
        _png_bytes((400, 200)),
        max_dimension=200,
    )
    assert result["width"] == 200
    assert result["height"] == 100


def test_resize_requires_an_option():
    try:
        image_service.resize(_png_bytes())
    except ValueError as error:
        assert "Provide" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_remove_metadata_reencodes_cleanly():
    result = image_service.remove_metadata(_jpg_bytes())
    assert result["extension"] == "jpg"
    assert isinstance(result["removed_metadata"], list)
    assert result["width"] == 120


def test_add_text_watermark():
    result = image_service.add_watermark(
        _png_bytes(),
        text="UTILS TOOLS",
        position="center",
    )
    assert result["extension"] == "webp"
    assert result["width"] == 120


def test_add_logo_watermark():
    result = image_service.add_watermark(
        _png_bytes(),
        logo_data=_png_bytes((20, 20)),
        rotation=45,
    )
    assert result["extension"] == "webp"


def test_watermark_requires_text_or_logo():
    try:
        image_service.add_watermark(_png_bytes())
    except ValueError as error:
        assert "Provide" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_watermark_rejects_bad_position():
    try:
        image_service.add_watermark(
            _png_bytes(),
            text="x",
            position="middle",
        )
    except ValueError as error:
        assert "position" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_background_replacement_with_color():
    image, width, height = background_service.replace_background(
        _png_bytes(),
        color="#00ff00",
    )
    assert (width, height) == (120, 80)
    assert image.size == (120, 80)


def test_background_replacement_with_image():
    image, width, height = background_service.replace_background(
        _png_bytes(),
        image_data=_png_bytes((40, 40)),
    )
    assert image.size == (120, 80)


def test_background_replacement_rejects_bad_image():
    try:
        background_service.replace_background(
            _png_bytes(),
            image_data=b"not an image",
        )
    except ValueError as error:
        assert "not valid" in str(error)
    else:
        raise AssertionError("Expected ValueError")
