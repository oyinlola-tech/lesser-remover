from io import BytesIO
from pathlib import Path
from PIL import Image
from app.infrastructure.image.rembg_adapter import rembg_adapter
from app.modules.background.background_repository import (
    background_repository,
)
from app.modules.image.image_service import image_service


class BackgroundService:
    def remove_background(
        self,
        file_data: bytes,
        original_filename: str,
    ) -> tuple[Image.Image, int, int]:
        image = Image.open(
            BytesIO(file_data),
        )
        image.load()
        width, height = image.size
        processed_image = (
            rembg_adapter.remove_background(
                image,
            )
        )
        return (
            processed_image,
            width,
            height,
        )


background_service = BackgroundService()
