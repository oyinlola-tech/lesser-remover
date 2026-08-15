from pydantic import BaseModel


class PdfToolResponse(BaseModel):
    success: bool
    filename: str
    size_bytes: int
    download_url: str
    details: dict = {}


class PdfPageFile(BaseModel):
    filename: str
    size_bytes: int
    download_url: str
    page: int


class PdfImagesResponse(BaseModel):
    success: bool
    image_format: str
    dpi: int
    page_count: int
    as_zip: bool
    filename: str | None = None
    size_bytes: int | None = None
    download_url: str | None = None
    details: dict = {}
    pages: list[PdfPageFile] = []


class PdfInfoResponse(BaseModel):
    success: bool
    filename: str
    page_count: int
    file_size_bytes: int
