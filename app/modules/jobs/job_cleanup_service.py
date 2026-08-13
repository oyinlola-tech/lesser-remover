import shutil
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.infrastructure.jobs import local_job_storage


class JobCleanupService:
    def cleanup_expired_jobs(self) -> int:
        now = datetime.now(timezone.utc)
        expiration = timedelta(
            minutes=settings.job_expiration_minutes
        )
        removed = 0
        if not local_job_storage.root_path.exists():
            return 0
        for job_path in (
            local_job_storage.root_path.iterdir()
        ):
            if not job_path.is_dir():
                continue
            metadata_path = (
                job_path / "metadata.json"
            )
            if not metadata_path.exists():
                shutil.rmtree(
                    job_path,
                    ignore_errors=True,
                )
                removed += 1
                continue
            try:
                metadata = (
                    local_job_storage.read_metadata(
                        job_path.name
                    )
                )
                timestamp = (
                    metadata.get("updated_at")
                    or metadata.get("created_at")
                )
                if not timestamp:
                    shutil.rmtree(
                        job_path,
                        ignore_errors=True,
                    )
                    removed += 1
                    continue
                updated_at = datetime.fromisoformat(
                    timestamp
                )
                if (
                    now - updated_at
                    > expiration
                ):
                    shutil.rmtree(
                        job_path,
                        ignore_errors=True,
                    )
                    removed += 1
            except (
                KeyError,
                ValueError,
                OSError,
            ):
                shutil.rmtree(
                    job_path,
                    ignore_errors=True,
                )
                removed += 1
        return removed

    def cleanup_expired_downloads(
        self,
    ) -> int:
        now = datetime.now(timezone.utc)
        expiration = timedelta(
            minutes=settings.job_expiration_minutes
        )
        removed = 0
        if not local_job_storage.download_path.exists():
            return 0
        for file_path in (
            local_job_storage.download_path.iterdir()
        ):
            if not file_path.is_file():
                continue
            try:
                modified_at = (
                    datetime.fromtimestamp(
                        file_path.stat().st_mtime,
                        tz=timezone.utc,
                    )
                )
                if (
                    now - modified_at
                    > expiration
                ):
                    file_path.unlink(
                        missing_ok=True
                    )
                    removed += 1
            except OSError:
                removed += 1
        return removed

    def cleanup_all(self) -> dict:
        return {
            "jobs_removed":
                self.cleanup_expired_jobs(),
            "downloads_removed":
                self.cleanup_expired_downloads(),
        }


job_cleanup_service = JobCleanupService()
