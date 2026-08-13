from app.core.config import settings

if settings.storage_driver == "vercel":
    from app.infrastructure.storage.vercel_storage import (
        vercel_storage as storage,
    )
else:
    from app.infrastructure.storage.local_storage import (
        storage,
    )

__all__ = ["storage"]
