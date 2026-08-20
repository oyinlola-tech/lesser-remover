"""Image tool services package.

Each image tool has its own service class in this package. The module-level
:data:`app.modules.image.image_service` facade delegates to these services so
controllers and tests keep a single entry point.
"""

from app.modules.image.services.converter_service import image_converter_service
from app.modules.image.services.cropper_service import image_cropper_service
from app.modules.image.services.metadata_remover_service import (
    metadata_remover_service,
)
from app.modules.image.services.palette_service import palette_extractor_service
from app.modules.image.services.resizer_service import image_resizer_service
from app.modules.image.services.watermark_service import watermark_service

__all__ = [
    "image_converter_service",
    "image_cropper_service",
    "image_resizer_service",
    "metadata_remover_service",
    "palette_extractor_service",
    "watermark_service",
]
