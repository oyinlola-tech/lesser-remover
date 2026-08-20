"""Facade over the per-tool image controllers.

Keeps a single ``image_tools_controller`` entry point for routes,
delegating each operation to its dedicated controller.
"""

from fastapi import UploadFile

from app.modules.image.controllers import (
    convert_controller,
    crop_controller,
    full_resize_controller,
    metadata_controller,
    palette_controller,
    resize_batch_controller,
    resize_controller,
    watermark_controller,
)


class ImageToolsController:
    """Delegates image tool operations to their per-tool controllers."""

    async def convert(self, file: UploadFile, *args, **kwargs):
        return await convert_controller.convert(file, *args, **kwargs)

    async def convert_batch(self, files: list[UploadFile], *args, **kwargs):
        return await convert_controller.convert_batch(files, *args, **kwargs)

    async def resize(self, file: UploadFile, *args, **kwargs):
        return await resize_controller.resize(file, *args, **kwargs)

    async def resize_image(self, file: UploadFile, *args, **kwargs):
        return await full_resize_controller.resize_image(file, *args, **kwargs)

    async def resize_batch(self, files: list[UploadFile], *args, **kwargs):
        return await resize_batch_controller.resize_batch(files, *args, **kwargs)

    async def crop(self, file: UploadFile, *args, **kwargs):
        return await crop_controller.crop(file, *args, **kwargs)

    async def remove_metadata(self, file: UploadFile):
        return await metadata_controller.remove_metadata(file)

    async def add_watermark(self, file: UploadFile, *args, **kwargs):
        return await watermark_controller.add_watermark(file, *args, **kwargs)

    async def extract_palette(self, file: UploadFile, *args, **kwargs):
        return await palette_controller.extract_palette(file, *args, **kwargs)


image_tools_controller = ImageToolsController()
