"""Tests for the Image Converter batch endpoint."""

from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _png_bytes(size=(120, 80), color=(255, 0, 0, 255)) -> bytes:
    buffer = BytesIO()
    Image.new("RGBA", size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def _jpg_bytes(size=(120, 80)) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", size, (10, 200, 30)).save(buffer, format="JPEG")
    return buffer.getvalue()


def _webp_bytes(size=(120, 80)) -> bytes:
    buffer = BytesIO()
    Image.new("RGBA", size, (0, 100, 255, 200)).save(buffer, format="WEBP")
    return buffer.getvalue()


def test_api_convert_single_png_to_jpeg():
    response = client.post(
        "/api/v1/images/convert",
        files=[("files", ("test.png", _png_bytes(), "image/png"))],
        data={"output_format": "jpg", "background_color": "#ffffff"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_files"] == 1
    assert body["successful_files"] == 1
    result = body["results"][0]
    assert result["output_format"] == "jpg"
    assert result["details"]["flattened"] is True


def test_api_convert_png_to_webp_preserves_alpha():
    response = client.post(
        "/api/v1/images/convert",
        files=[("files", ("test.png", _png_bytes(), "image/png"))],
        data={"output_format": "webp"},
    )
    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["output_format"] == "webp"
    assert result["details"]["has_alpha"] is True


def test_api_convert_jpeg_to_png():
    response = client.post(
        "/api/v1/images/convert",
        files=[("files", ("photo.jpg", _jpg_bytes(), "image/jpeg"))],
        data={"output_format": "png"},
    )
    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["input_format"] == "JPEG"
    assert result["output_format"] == "png"
    assert result["width"] == 120
    assert result["height"] == 80


def test_api_convert_webp_to_jpeg():
    response = client.post(
        "/api/v1/images/convert",
        files=[("files", ("img.webp", _webp_bytes(), "image/webp"))],
        data={"output_format": "jpg", "background_color": "#000000"},
    )
    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["output_format"] == "jpg"


def test_api_convert_multiple_files():
    response = client.post(
        "/api/v1/images/convert",
        files=[
            ("files", ("a.png", _png_bytes(), "image/png")),
            ("files", ("b.jpg", _jpg_bytes(), "image/jpeg")),
        ],
        data={"output_format": "webp"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_files"] == 2
    assert body["successful_files"] == 2
    assert body["failed_files"] == 0


def test_api_convert_per_file_failure():
    response = client.post(
        "/api/v1/images/convert",
        files=[
            ("files", ("good.png", _png_bytes(), "image/png")),
            ("files", ("bad.png", b"not an image", "image/png")),
        ],
        data={"output_format": "webp"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["successful_files"] == 1
    assert body["failed_files"] == 1
    assert body["failures"][0]["filename"] == "bad.png"


def test_api_convert_rejects_invalid_format():
    response = client.post(
        "/api/v1/images/convert",
        files=[("files", ("test.png", _png_bytes(), "image/png"))],
        data={"output_format": "tiff"},
    )
    assert response.status_code == 400


def test_api_convert_rejects_invalid_quality():
    response = client.post(
        "/api/v1/images/convert",
        files=[("files", ("test.png", _png_bytes(), "image/png"))],
        data={"output_format": "jpg", "quality": "150"},
    )
    assert response.status_code == 400


def test_api_convert_rejects_too_many_files():
    files = [
        ("files", (f"img{i}.png", _png_bytes(), "image/png"))
        for i in range(51)
    ]
    response = client.post(
        "/api/v1/images/convert",
        files=files,
        data={"output_format": "webp"},
    )
    assert response.status_code == 400


def test_api_convert_with_quality():
    # Create a noisier image so quality affects file size
    import random
    random.seed(42)
    buffer = BytesIO()
    img = Image.new("RGB", (400, 300))
    pixels = img.load()
    for x in range(400):
        for y in range(300):
            pixels[x, y] = (
                (x * 3) % 256,
                (y * 5) % 256,
                ((x + y) * 2) % 256,
            )
    img.save(buffer, format="JPEG")
    noisy_jpg = buffer.getvalue()

    response = client.post(
        "/api/v1/images/convert",
        files=[("files", ("test.jpg", noisy_jpg, "image/jpeg"))],
        data={"output_format": "jpg", "quality": "30"},
    )
    result_low = response.json()["results"][0]

    response2 = client.post(
        "/api/v1/images/convert",
        files=[("files", ("test2.jpg", noisy_jpg, "image/jpeg"))],
        data={"output_format": "jpg", "quality": "95"},
    )
    result_high = response2.json()["results"][0]

    assert result_low["size_bytes"] < result_high["size_bytes"]


def test_api_convert_dimensions_preserved():
    response = client.post(
        "/api/v1/images/convert",
        files=[("files", ("test.png", _png_bytes(), "image/png"))],
        data={"output_format": "webp"},
    )
    result = response.json()["results"][0]
    assert result["original_width"] == result["width"]
    assert result["original_height"] == result["height"]


def test_api_convert_download_url():
    response = client.post(
        "/api/v1/images/convert",
        files=[("files", ("test.png", _png_bytes(), "image/png"))],
        data={"output_format": "png"},
    )
    result = response.json()["results"][0]
    assert result["download_url"].startswith("/api/v1/tools/image/download/")


def test_api_convert_rejects_no_files():
    response = client.post(
        "/api/v1/images/convert",
        files=[],
        data={"output_format": "webp"},
    )
    assert response.status_code in (400, 422)
