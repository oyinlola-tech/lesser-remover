"""Composition module exposing the background router."""

from fastapi import APIRouter

from app.modules.background.routes.process_route import (
    create_process_router,
)
from app.modules.background.routes.result_route import (
    create_result_router,
)

router = APIRouter(tags=["Background Removal"])

for _subrouter in (
    create_process_router(),
    create_result_router(),
):
    router.include_router(_subrouter)
