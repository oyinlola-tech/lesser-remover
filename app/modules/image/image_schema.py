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


class ResizeResult(BaseModel):
    success: bool
    original_filename: str
    output_filename: str
    input_format: str
    output_format: str
    original_width: int
    original_height: int
    width: int
    height: int
    original_size_bytes: int
    size_bytes: int
    download_url: str
    details: dict = {}


class ResizeFailure(BaseModel):
    filename: str
    error: str


class ResizeBatchResult(BaseModel):
    success: bool
    total_files: int
    successful_files: int
    failed_files: int
    results: list[ResizeResult]
    failures: list[ResizeFailure] = []


class ConvertResult(BaseModel):
    success: bool
    original_filename: str
    output_filename: str
    input_format: str
    output_format: str
    original_width: int
    original_height: int
    width: int
    height: int
    original_size_bytes: int
    size_bytes: int
    download_url: str
    details: dict = {}


class ConvertBatchResult(BaseModel):
    success: bool
    total_files: int
    successful_files: int
    failed_files: int
    results: list[ConvertResult]
    failures: list[ResizeFailure] = []
