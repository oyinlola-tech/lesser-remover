"""Validation schemas for Video Downloader API endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


class VideoInfoRequest(BaseModel):
    """Payload for fetching video metadata."""

    url: str = Field(..., description="Target video URL (YouTube, TikTok, Facebook, Instagram, Twitter, etc.)")


class VideoDownloadRequest(BaseModel):
    """Payload for initiating a video download."""

    url: str = Field(..., description="Target video URL")
    format: Literal["mp4", "mp3", "webm", "m4a"] = Field(
        default="mp4", description="Output format (mp4 for video, mp3 for audio)"
    )
    quality: Literal["best", "1080p", "720p", "480p", "audio"] = Field(
        default="best", description="Resolution or quality preference"
    )
