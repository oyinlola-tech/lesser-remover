from app.core.config import settings

if settings.storage_driver == "vercel":
    from app.infrastructure.jobs.vercel_job_storage import (
        vercel_job_storage as local_job_storage,
    )
else:
    from app.infrastructure.jobs.local_job_storage import (
        local_job_storage,
    )

__all__ = ["local_job_storage"]
