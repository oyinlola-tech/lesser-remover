"""Unit tests for Video Downloader schema, service, controller, and routes."""

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.video.video_schema import VideoDownloadRequest, VideoInfoRequest
from app.modules.video.video_service import video_downloader_service
from app.core.exceptions import ProcessingError

client = TestClient(app)


def test_video_info_schema_validation():
    """Test VideoInfoRequest payload validation."""
    req = VideoInfoRequest(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert req.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_video_download_schema_validation():
    """Test VideoDownloadRequest defaults and choices."""
    req = VideoDownloadRequest(url="https://tiktok.com/@user/video/12345")
    assert req.format == "mp4"
    assert req.quality == "best"

    req_audio = VideoDownloadRequest(
        url="https://youtube.com/watch?v=abc", format="mp3", quality="audio"
    )
    assert req_audio.format == "mp3"
    assert req_audio.quality == "audio"


@patch("yt_dlp.YoutubeDL")
def test_video_service_get_info_success(mock_ytdl):
    """Test get_video_info service method returning formatted dict."""
    mock_instance = MagicMock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.return_value = {
        "title": "Sample Video",
        "uploader": "Test Channel",
        "duration": 125,
        "thumbnail": "https://example.com/thumb.jpg",
        "extractor_key": "Youtube",
        "formats": [{"height": 1080}, {"height": 720}, {"height": 480}],
    }

    result = video_downloader_service.get_video_info("https://youtube.com/watch?v=test")

    assert result["title"] == "Sample Video"
    assert result["uploader"] == "Test Channel"
    assert result["duration_seconds"] == 125
    assert result["duration_formatted"] == "02:05"
    assert result["platform"] == "Youtube"
    assert "1080p" in result["available_qualities"]


@patch("yt_dlp.YoutubeDL")
def test_video_service_get_info_error(mock_ytdl):
    """Test get_video_info handling yt-dlp error."""
    import yt_dlp

    mock_instance = MagicMock()
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    mock_instance.extract_info.side_effect = yt_dlp.utils.DownloadError("Invalid URL")

    with pytest.raises(ProcessingError) as exc_info:
        video_downloader_service.get_video_info("https://invalid-link.com")
    
    assert "Could not retrieve video details" in str(exc_info.value)


def test_api_video_info_endpoint():
    """Test POST /api/v1/tools/video/info API route."""
    with patch("app.modules.video.video_service.video_downloader_service.get_video_info") as mock_info:
        mock_info.return_value = {
            "url": "https://youtube.com/watch?v=123",
            "title": "Mock Video",
            "uploader": "Mock User",
            "duration_seconds": 60,
            "duration_formatted": "01:00",
            "thumbnail": "http://img.png",
            "platform": "Youtube",
            "available_qualities": ["720p"],
        }

        response = client.post(
            "/api/v1/tools/video/info",
            json={"url": "https://youtube.com/watch?v=123"},
        )

        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert json_data["data"]["title"] == "Mock Video"


def test_api_video_download_endpoint():
    """Test POST /api/v1/tools/video/download API route."""
    from pathlib import Path

    with patch("app.modules.video.video_service.video_downloader_service.download_video") as mock_dl:
        mock_dl.return_value = Path("storage/temp/video_test_sample.mp4")

        with patch("pathlib.Path.exists", return_value=True), patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value.st_size = 1048576

            response = client.post(
                "/api/v1/tools/video/download",
                json={
                    "url": "https://youtube.com/watch?v=123",
                    "format": "mp4",
                    "quality": "720p",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "video_test_sample.mp4" in data["filename"]
            assert data["download_url"].endswith("/api/v1/tools/video/download/video_test_sample.mp4")
            assert data["download_url"].startswith("http://testserver/")
