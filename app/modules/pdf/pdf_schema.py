from pydantic import BaseModel


class PdfToolResponse(BaseModel):
    success: bool
    filename: str
    size_bytes: int
    download_url: str
    details: dict = {}


class PdfInfoResponse(BaseModel):
    success: bool
    filename: str
    page_count: int
    file_size_bytes: int
