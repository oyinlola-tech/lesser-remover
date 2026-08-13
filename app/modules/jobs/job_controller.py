from fastapi import HTTPException

from app.modules.jobs.job_service import (
    job_service,
)


class JobController:
    def get_job(self, job_id: str) -> dict:
        job = job_service.get(job_id)
        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found.",
            )
        return job


job_controller = JobController()
