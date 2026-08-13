from pydantic import BaseModel


class BackgroundRemovalResponse(BaseModel):
    success: bool
    original_filename: str
    width: int
    height: int
    format: str
    filename: str
    size_bytes: int
    download_url: str


class BackgroundDownloadResponse(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
