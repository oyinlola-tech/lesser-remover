from enum import Enum


class FileType(str, Enum):
    IMAGE = "image"
    PDF = "pdf"
    ARCHIVE = "archive"
    DOCUMENT = "document"
    UNKNOWN = "unknown"