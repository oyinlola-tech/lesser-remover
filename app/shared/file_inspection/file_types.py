from enum import StrEnum


class FileCategory(StrEnum):
    IMAGE = "image"
    PDF = "pdf"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"


class SupportedImageType(StrEnum):
    JPEG = "image/jpeg"
    PNG = "image/png"
    WEBP = "image/webp"
    GIF = "image/gif"
    BMP = "image/bmp"
    TIFF = "image/tiff"


class SupportedFileType(StrEnum):
    JPEG = "image/jpeg"
    PNG = "image/png"
    WEBP = "image/webp"
    GIF = "image/gif"
    BMP = "image/bmp"
    TIFF = "image/tiff"

    PDF = "application/pdf"
