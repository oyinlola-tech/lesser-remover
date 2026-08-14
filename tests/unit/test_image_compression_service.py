from io import BytesIO

from PIL import Image

from app.modules.compression.compression_settings import CompressionSettings
from app.modules.compression.image_compression.image_compression_service import (
    image_compression_service,
)
from app.modules.compression.image_compression.image_compression_settings import (
    PRESETS,
)


def make_test_image(width=800, height=600, color=(255, 0, 0)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()


def test_compress_with_preset_returns_expected_shape():
    data = make_test_image(1200, 900)
    for preset, settings in PRESETS.items():
        (
            compressed_data,
            content_type,
            quality,
            width,
            height,
        ) = image_compression_service.compress_with_preset(
            file_data=data,
            preset=preset,
            output_format=settings.default_format,
        )
        assert isinstance(compressed_data, (bytes, bytearray))
        assert content_type in ("image/webp", "image/jpeg", "image/png")
        assert quality in settings.qualities
        assert width == 1200
        assert height == 900


def test_compress_to_target_produces_quality_value():
    data = make_test_image(2000, 1500)
    target_bytes = 60 * 1024
    (
        compressed_data,
        content_type,
        quality,
        _width,
        _height,
    ) = image_compression_service.compress_to_target(
        file_data=data,
        target_size_bytes=target_bytes,
        output_format="webp",
    )
    assert isinstance(compressed_data, (bytes, bytearray))
    assert content_type == "image/webp"
    assert 20 <= quality <= 100
    # The returned data should not be larger than original (engine should avoid enlarging)
    assert len(compressed_data) <= len(data)


def test_compress_to_target_rejects_png():
    import pytest

    data = make_test_image(400, 300)
    with pytest.raises(ValueError):
        image_compression_service.compress_to_target(
            file_data=data,
            target_size_bytes=1024,
            output_format="png",
        )


def test_compression_settings_defaults_are_consumer_friendly():
    settings = CompressionSettings()

    assert settings.preset == "balanced"
    assert settings.output_format == "webp"
    assert settings.max_dimension is None
    assert settings.target_size_kb is None
    assert settings.strip_metadata is True
