from fastapi import APIRouter

from app.core.capabilities import capability_registry
from app.core.config import settings

router = APIRouter(
    prefix="/api/v1/capabilities",
    tags=["Capabilities"],
)


@router.get("")
async def get_capabilities():
    """Public capability information for the current environment.

    Safe to expose: no secrets, tokens, or environment variables.
    """
    return {
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
        },
        "storage_driver": capability_registry.driver,
        "system": capability_registry.system_capabilities(),
        "tools": capability_registry.effective_tools(),
    }
