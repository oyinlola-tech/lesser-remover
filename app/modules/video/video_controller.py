"""Controller for video downloader API operations."""

import logging
from pathlib import Path
from typing import Any, Dict
from urllib.parse import quote

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.exceptions import ProcessingError
from app.modules.video.video_schema import VideoDownloadRequest, VideoInfoRequest
from app.modules.video.video_service import video_downloader_service

logger = logging.getLogger(__name__)


class VideoDownloaderController:
    """Handles HTTP API routing logic for video downloader operations."""

    def get_info(self, request: VideoInfoRequest) -> Dict[str, Any]:
        """Retrieve video details without downloading."""
        if not request.url or not request.url.strip():
            raise HTTPException(status_code=400, detail="Video URL must not be empty.")

        try:
            info = video_downloader_service.get_video_info(request.url.strip())
            return {
                "success": True,
                "data": info,
            }
        except ProcessingError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except Exception as exc:
            logger.error("Controller error in get_info: %s", str(exc))
            raise HTTPException(status_code=500, detail="Failed to retrieve video information.")

    def download(self, request: Request, body: VideoDownloadRequest) -> Dict[str, Any]:
        """Download video/audio to server and return download metadata."""
        if not body.url or not body.url.strip():
            raise HTTPException(status_code=400, detail="Video URL must not be empty.")

        try:
            file_path = video_downloader_service.download_video(
                url=body.url.strip(),
                format_choice=body.format,
                quality_choice=body.quality,
            )

            file_size = file_path.stat().st_size if file_path.exists() else 0
            filename = file_path.name

            return {
                "success": True,
                "filename": filename,
                "size_bytes": file_size,
                "download_url": str(
                    request.url_for(
                        "download_video_file",
                        filename=quote(filename, safe=""),
                    )
                ),
            }
        except ProcessingError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except Exception as exc:
            logger.error("Controller error in download: %s", str(exc))
            raise HTTPException(status_code=500, detail="Failed to process video download.")

    def serve_file(self, filename: str) -> FileResponse:
        """Serve downloaded video or audio file for client download."""
        download_dir = Path(settings.temp_directory)
        file_path = download_dir / filename

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found or expired.")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/octet-stream",
        )


video_downloader_controller = VideoDownloaderController()
