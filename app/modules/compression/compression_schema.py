from pydantic import BaseModel


class CompressionResult(BaseModel):
    success: bool
    original_filename: str
    output_filename: str
    original_size_bytes: int
    compressed_size_bytes: int
    compression_ratio: float
    savings_percent: float
    content_type: str
    download_url: str
    output_format: str | None = None
    width: int | None = None
    height: int | None = None
    quality: int | None = None


class BatchCompressionResult(BaseModel):
    success: bool
    total_files: int
    successful_files: int
    failed_files: int
    original_size_bytes: int
    compressed_size_bytes: int
    savings_percent: float
    files: list[CompressionResult]
    download_all_url: str | None = None
