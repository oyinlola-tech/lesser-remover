from pydantic import BaseModel


class ImageVariant(BaseModel):
    format: str
    filename: str
    size_bytes: int
    download_url: str


class ProcessedImageResult(BaseModel):
    width: int
    height: int
    variants: list[ImageVariant]


class ImageToolResult(BaseModel):
    success: bool
    original_filename: str
    width: int
    height: int
    format: str
    filename: str
    size_bytes: int
    download_url: str
    details: dict = {}


class ImageToolListResult(BaseModel):
    success: bool
    items: list[ImageToolResult]


class MetadataRemovalResult(ImageToolResult):
    removed_metadata: list[str] = []
