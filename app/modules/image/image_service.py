from io import BytesIO
from pathlib import Path
from PIL import Image
from app.modules.image.image_processor import image_processor
from app.shared.utils.file_util import generate_filename


class ImageService:
    def generate_background_variants(
        self,
        image: Image.Image,
        original_filename: str,
    ) -> list[tuple[str, str, bytes]]:
        png_data = image_processor.create_png(
            image,
        )
        webp_data = image_processor.create_webp(
            image,
            quality=95,
        )
        png_filename = generate_filename(
            original_filename,
            extension="png",
        )
        webp_filename = generate_filename(
            original_filename,
            extension="webp",
        )
        return [
            (
                "png",
                png_filename,
                png_data,
            ),
            (
                "webp",
                webp_filename,
                webp_data,
            ),
        ]


image_service = ImageService()
