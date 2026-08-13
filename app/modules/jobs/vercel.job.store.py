from app.infrastructure.jobs.local_job_storage import LocalJobStorage


class VercelJobStore:
    def __init__(self) -> None:
        self._storage = LocalJobStorage()
