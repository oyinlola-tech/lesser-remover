from enum import StrEnum


class CompressionLevel(StrEnum):
    BEST_QUALITY = "best_quality"
    BALANCED = "balanced"
    SMALLEST = "smallest"


class PdfCompressionLevel(StrEnum):
    BEST_QUALITY = "printer"
    BALANCED = "ebook"
    SMALLEST = "screen"
