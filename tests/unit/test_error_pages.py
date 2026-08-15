"""Tests for designed error pages and the rate limiter."""

from fastapi.testclient import TestClient

from app.core import middleware as middleware_module
from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_browser_404_returns_designed_page():
    response = client.get(
        "/no-such-page",
        headers={"Accept": "text/html"},
    )
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("text/html")
    assert "This page doesn't exist." in response.text
    assert 'class="error-code"' in response.text


def test_api_404_returns_json_envelope():
    response = client.get("/api/v1/no-such-api")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["status"] == 404


def test_error_pages_serve_with_matching_status():
    cases = {
        "/errors/404.html": 404,
        "/errors/413.html": 413,
        "/errors/422.html": 422,
        "/errors/429.html": 429,
        "/errors/500.html": 500,
    }
    for path, expected in cases.items():
        response = client.get(path, headers={"Accept": "text/html"})
        assert response.status_code == expected
        assert response.headers["content-type"].startswith("text/html")
        assert 'class="error-code"' in response.text


def test_utility_error_pages_serve_ok():
    for path in ("/errors/tool-error.html", "/errors/offline.html"):
        response = client.get(path, headers={"Accept": "text/html"})
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")


def test_auth_error_pages_removed():
    response = client.get("/errors/401.html", headers={"Accept": "text/html"})
    assert response.status_code == 404


def test_rate_limit_returns_429(monkeypatch):
    middleware_module._RATE_LIMIT_BUCKETS.clear()
    monkeypatch.setattr(settings, "app_env", "production")
    monkeypatch.setattr(settings, "rate_limit_max_requests", 3)
    monkeypatch.setattr(settings, "rate_limit_window_seconds", 60)

    limited_client = TestClient(app)
    for _ in range(3):
        response = limited_client.get("/api/v1/capabilities")
        assert response.status_code == 200

    response = limited_client.get("/api/v1/capabilities")
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    body = response.json()
    assert body["error"]["code"] == "RATE_LIMITED"
    assert body["error"]["status"] == 429
    middleware_module._RATE_LIMIT_BUCKETS.clear()
