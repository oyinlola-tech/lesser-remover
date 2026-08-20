"""Image tool controllers package.

Each image tool gets its own controller; :data:`ImageToolsController`
composes them so routes keep a single entry point.
"""

from app.modules.image.controllers.convert_controller import convert_controller
from app.modules.image.controllers.crop_controller import crop_controller
from app.modules.image.controllers.metadata_controller import metadata_controller
from app.modules.image.controllers.palette_controller import palette_controller
from app.modules.image.controllers.resize_controller import resize_controller
from app.modules.image.controllers.watermark_controller import watermark_controller

__all__ = [
    "convert_controller",
    "crop_controller",
    "metadata_controller",
    "palette_controller",
    "resize_controller",
    "watermark_controller",
]
