"""Composition module exposing the compression start routers."""

from app.modules.compression.routes.compress_images_route import (
    create_images_compress_router,
)
from app.modules.compression.routes.start_batch_route import (
    create_batch_start_router,
)

create_compression_router = create_batch_start_router
create_image_router = create_images_compress_router
