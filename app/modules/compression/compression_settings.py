from dataclasses import dataclass


@dataclass(frozen=True)
class CompressionSettings:
    preset: str = "balanced"
    quality: int | None = None
    output_format: str = "webp"
    max_dimension: int | None = None
    target_size_kb: int | None = None
    strip_metadata: bool = True
