"""Composes the per-tool image routers into the public API routers.

``router`` serves the legacy ``/api/v1/tools/image`` endpoints and
``images_router`` the ``/api/v1/images`` batch endpoints.
"""

from fastapi import APIRouter

from app.api import API_PREFIX
from app.modules.image.routes import (
    convert_batch_router,
    convert_router,
    crop_router,
    misc_router,
    resize_batch_router,
    resize_router,
)

router = APIRouter(
    prefix=f"{API_PREFIX}/tools/image",
    tags=["Image Tools"],
)

images_router = APIRouter(
    prefix=f"{API_PREFIX}/images",
    tags=["Image Tools"],
)

router.include_router(convert_router)
router.include_router(resize_router)
router.include_router(crop_router)
router.include_router(misc_router)
images_router.include_router(convert_batch_router)
images_router.include_router(resize_batch_router)
