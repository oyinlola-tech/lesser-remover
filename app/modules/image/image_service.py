"""Facade over the per-tool image services.

Keeps a single ``image_service`` entry point for controllers and tests,
delegating each operation to its dedicated service.
"""

from PIL import Image

from app.modules.image.image_processor import image_processor
from app.modules.image.services import (
    image_converter_service,
    image_cropper_service,
    image_resizer_service,
    metadata_remover_service,
    palette_extractor_service,
    watermark_service,
)
from app.shared.utils.file_util import generate_filename


class ImageService:
    """Delegates image operations to their per-tool services."""

    def convert(self, *args, **kwargs) -> dict:
        return image_converter_service.convert(*args, **kwargs)

    def resize(self, *args, **kwargs) -> dict:
        return image_resizer_service.resize(*args, **kwargs)

    def crop(self, *args, **kwargs) -> dict:
        return image_cropper_service.crop(*args, **kwargs)

    def remove_metadata(self, file_data: bytes) -> dict:
        return metadata_remover_service.remove_metadata(file_data)

    def add_watermark(self, *args, **kwargs) -> dict:
        return watermark_service.add_watermark(*args, **kwargs)

    def extract_palette(self, image_data: bytes, num_colors: int = 6) -> list[dict]:
        return palette_extractor_service.extract_palette(image_data, num_colors)

    def generate_background_variants(
        self,
        image: Image.Image,
        original_filename: str,
    ) -> list[tuple[str, str, bytes]]:
        png_data = image_processor.create_png(image)
        webp_data = image_processor.create_webp(image, quality=95)
        return [
            ("png", generate_filename(original_filename, extension="png"), png_data),
            ("webp", generate_filename(original_filename, extension="webp"), webp_data),
        ]


image_service = ImageService()
