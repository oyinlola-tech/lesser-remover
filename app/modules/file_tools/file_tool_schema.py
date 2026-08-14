from pydantic import BaseModel


class FileAnalysis(BaseModel):
    filename: str
    size_bytes: int
    mime_type: str
    category: str
    extension: str
    sha256: str
    width: int | None = None
    height: int | None = None
    page_count: int | None = None


class FileAnalysisResponse(BaseModel):
    success: bool
    files: list[FileAnalysis]


class FileToolResponse(BaseModel):
    success: bool
    filename: str
    size_bytes: int
    download_url: str
    details: dict = {}


class DuplicateReport(BaseModel):
    hash: str
    filenames: list[str]
    size_bytes: int
