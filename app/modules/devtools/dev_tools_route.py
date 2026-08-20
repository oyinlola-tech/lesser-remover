"""Composes the per-tool devtools routers into the public API router."""

from fastapi import APIRouter

from app.api import API_PREFIX
from app.modules.devtools.routes import (
    data_router,
    favicon_router,
    image_gen_router,
    svg_router,
)

router = APIRouter(
    prefix=f"{API_PREFIX}/tools/dev",
    tags=["Developer Tools"],
)

router.include_router(favicon_router)
router.include_router(svg_router)
router.include_router(image_gen_router)
router.include_router(data_router)
