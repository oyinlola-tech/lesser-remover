from dataclasses import dataclass


@dataclass(frozen=True)
class ImageCompressionSettings:
    qualities: tuple[int, ...]
    default_format: str
    max_dimension: int | None = None


PRESETS = {
    "best_quality": ImageCompressionSettings(
        qualities=(100, 98, 95, 92),
        default_format="webp",
    ),

    "balanced": ImageCompressionSettings(
        qualities=(95, 90, 85, 80),
        default_format="webp",
    ),

    "smallest": ImageCompressionSettings(
        qualities=(85, 80, 75, 70, 65, 60),
        default_format="webp",
    ),
}
