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
