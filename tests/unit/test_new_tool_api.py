"""API-level tests for the new tool endpoints (Phases 4-9)."""

from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGBA", (60, 40), (255, 0, 0, 255)).save(
        buffer,
        format="PNG",
    )
    return buffer.getvalue()


def _pdf_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (100, 100), (255, 255, 255)).save(
        buffer,
        format="PDF",
    )
    return buffer.getvalue()


def test_image_convert_endpoint():
    response = client.post(
        "/api/v1/tools/image/convert",
        files={"file": ("photo.png", _png_bytes(), "image/png")},
        data={"output_format": "webp"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["download_url"].startswith("/api/v1/tools/image/download/")


def test_image_resize_endpoint_rejects_bad_percent():
    response = client.post(
        "/api/v1/tools/image/resize",
        files={"file": ("photo.png", _png_bytes(), "image/png")},
        data={"percent": "0"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_REQUEST"


def test_metadata_remover_endpoint():
    response = client.post(
        "/api/v1/tools/image/remove-metadata",
        files={"file": ("photo.png", _png_bytes(), "image/png")},
    )
    assert response.status_code == 200


def test_watermark_endpoint_requires_input():
    response = client.post(
        "/api/v1/tools/image/watermark",
        files={"file": ("photo.png", _png_bytes(), "image/png")},
    )
    assert response.status_code == 400


def test_background_replacement_endpoint():
    response = client.post(
        "/api/v1/background/replace",
        files={"file": ("photo.png", _png_bytes(), "image/png")},
        data={"color": "#9fe870"},
    )
    assert response.status_code == 200
    assert response.json()["result"]["format"] == "png"


def test_pdf_merge_endpoint():
    response = client.post(
        "/api/v1/tools/pdf/merge",
        files=[
            ("files", ("a.pdf", _pdf_bytes(), "application/pdf")),
            ("files", ("b.pdf", _pdf_bytes(), "application/pdf")),
        ],
    )
    assert response.status_code == 200
    assert response.json()["details"]["page_count"] == 2


def test_pdf_rotate_endpoint_validates_angle():
    response = client.post(
        "/api/v1/tools/pdf/rotate",
        files={"file": ("a.pdf", _pdf_bytes(), "application/pdf")},
        data={"angle": "45"},
    )
    assert response.status_code == 400


def test_pdf_extract_endpoint_validates_pages():
    response = client.post(
        "/api/v1/tools/pdf/extract",
        files={"file": ("a.pdf", _pdf_bytes(), "application/pdf")},
        data={"pages": "99"},
    )
    assert response.status_code == 400


def test_image_to_pdf_endpoint():
    response = client.post(
        "/api/v1/tools/pdf/from-images",
        files=[
            ("files", ("a.png", _png_bytes(), "image/png")),
            ("files", ("b.png", _png_bytes(), "image/png")),
        ],
    )
    assert response.status_code == 200
    assert response.json()["details"]["page_count"] == 2


def test_file_analyze_endpoint():
    response = client.post(
        "/api/v1/tools/file/analyze",
        files=[("files", ("a.png", _png_bytes(), "image/png"))],
    )
    assert response.status_code == 200
    assert response.json()["files"][0]["category"] == "image"


def test_file_zip_endpoint():
    response = client.post(
        "/api/v1/tools/file/zip",
        files=[("files", ("a.png", _png_bytes(), "image/png"))],
    )
    assert response.status_code == 200
    assert response.json()["filename"].endswith(".zip")


def test_file_duplicates_endpoint():
    response = client.post(
        "/api/v1/tools/file/duplicates",
        files=[
            ("files", ("a.png", _png_bytes(), "image/png")),
            ("files", ("b.png", _png_bytes(), "image/png")),
        ],
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_favicon_endpoint_returns_zip():
    response = client.post(
        "/api/v1/tools/dev/favicon",
        files={"image": ("a.png", _png_bytes(), "image/png")},
        data={"size": "64"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"


def test_svg_optimizer_endpoint():
    response = client.post(
        "/api/v1/tools/dev/svg-optimize",
        files={
            "file": (
                "a.svg",
                b'<svg xmlns="http://www.w3.org/2000/svg"><!-- c --><path d="M 0 0"/></svg>',
                "image/svg+xml",
            )
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"


def test_qr_endpoint():
    response = client.post(
        "/api/v1/tools/dev/qr",
        data={"content": "https://example.com"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_barcode_endpoint():
    response = client.post(
        "/api/v1/tools/dev/barcode",
        data={"content": "HELLO-123"},
    )
    assert response.status_code == 200


def test_social_presets_endpoint():
    response = client.get("/api/v1/tools/image/social-presets")
    assert response.status_code == 200
    presets = response.json()["presets"]
    assert len(presets) >= 10
    first = presets[0]
    assert first["width"] > 0 and first["height"] > 0


def test_tool_pages_all_serve():
    import glob

    for path in sorted(glob.glob("frontend/pages/*.html")):
        tool_id = path.split("/")[-1].replace(".html", "")
        response = client.get(f"/tools/{tool_id}")
        assert response.status_code == 200, tool_id
        js_response = client.get(f"/static/assets/js/pages/{tool_id}.js")
        assert js_response.status_code == 200, tool_id
