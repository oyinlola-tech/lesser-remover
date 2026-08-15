from PIL import Image

from app.infrastructure.compression.pillow_adapter import (
    pillow_adapter,
)


class ImageProcessor:
    def create_png(
        self,
        image: Image.Image,
    ) -> bytes:
        return pillow_adapter.encode_png(image)

    def create_webp(
        self,
        image: Image.Image,
        quality: int = 95,
    ) -> bytes:
        return pillow_adapter.encode_webp(
            image,
            quality=quality,
        )

    def create_jpeg(
        self,
        image: Image.Image,
        quality: int = 95,
    ) -> bytes:
        return pillow_adapter.encode_jpeg(
            image,
            quality=quality,
        )


image_processor = ImageProcessor()
