from datetime import datetime

from pydantic import BaseModel


class JobFile(BaseModel):
    id: str
    filename: str
    input_filename: str = ""
    status: str

    original_size_bytes: int = 0
    compressed_size_bytes: int = 0
    savings_percent: float = 0

    output_filename: str = ""
    download_url: str = ""
    content_type: str = ""

    output_format: str = ""
    quality: int | None = None
    compression_preset: str = ""
    width: int | None = None
    height: int | None = None

    target_size_bytes: int | None = None
    target_achieved: bool = False

    error: str | None = None


class Job(BaseModel):
    job_id: str
    status: str
    created_at: datetime

    total_files: int = 0
    completed_files: int = 0
    failed_files: int = 0

    original_size_bytes: int = 0
    compressed_size_bytes: int = 0

    files: list[JobFile] = []
    download_url: str | None = None
