"""Composition module exposing the compression routers."""

from app.modules.compression.routes.download_route import (
    create_download_router,
)
from app.modules.compression.routes.start_compression_routes import (
    create_compression_router,
    create_image_router,
)

router = create_compression_router()
image_router = create_image_router()
download_router = create_download_router()

router.include_router(download_router)
