"""Composition module exposing the PDF tools router."""

from fastapi import APIRouter

from app.modules.pdf.routes.download_route import (
    create_download_router,
)
from app.modules.pdf.routes.encrypt_route import (
    create_encrypt_router,
)
from app.modules.pdf.routes.extract_route import (
    create_extract_router,
)
from app.modules.pdf.routes.from_images_route import (
    create_from_images_router,
)
from app.modules.pdf.routes.info_route import (
    create_info_router,
)
from app.modules.pdf.routes.merge_route import (
    create_merge_router,
)
from app.modules.pdf.routes.page_number_route import (
    create_page_number_router,
)
from app.modules.pdf.routes.rotate_route import (
    create_rotate_router,
)
from app.modules.pdf.routes.split_route import (
    create_split_router,
)
from app.modules.pdf.routes.to_images_route import (
    create_to_images_router,
)
from app.modules.pdf.routes.watermark_route import (
    create_watermark_router,
)

router = APIRouter(tags=["PDF Tools"])

for _subrouter in (
    create_merge_router(),
    create_split_router(),
    create_rotate_router(),
    create_extract_router(),
    create_to_images_router(),
    create_from_images_router(),
    create_info_router(),
    create_encrypt_router(),
    create_page_number_router(),
    create_watermark_router(),
    create_download_router(),
):
    router.include_router(_subrouter)
