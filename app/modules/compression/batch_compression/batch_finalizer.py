"""Job finalization: zip outputs and set the download URL."""

import logging

from app.infrastructure.jobs import local_job_storage
from app.modules.archive.archive_service import (
    archive_service,
)
from app.modules.jobs.job_service import (
    job_service,
)

logger = logging.getLogger(__name__)


class BatchFinalizer:

    def finalize_job(
        self,
        job_id: str,
    ) -> None:

        if job_service.is_cancelled(job_id):
            logger.info(
                "Job %s was cancelled, skipping finalization",
                job_id,
            )
            return

        metadata = job_service.get(job_id)

        logger.info(
            "Finalizing job %s: status=%s, completed=%s, failed=%s",
            job_id,
            metadata.get("status"),
            metadata.get("completed_files"),
            metadata.get("failed_files"),
        )

        output_directory = local_job_storage.get_output_path(job_id)

        output_files = [
            path
            for path in output_directory.iterdir()
            if path.is_file()
        ]

        if not output_files:
            job_service.update_status(job_id, "failed")
            return

        try:
            zip_filename = f"compressed_{job_id}.zip"

            zip_path = (
                local_job_storage.get_job_path(job_id)
                / zip_filename
            )

            archive_service.create_zip_from_directory(
                output_directory,
                zip_path,
            )

            download_path = local_job_storage.move_download(
                zip_path,
                zip_filename,
            )

            job_service.set_download_url(
                job_id,
                "/api/v1/compression/download/"
                f"{download_path.name}",
            )
        except Exception as error:
            logger.exception(
                "Failed to finalize job %s: %s",
                job_id,
                error,
            )
            job_service.update_status(job_id, "failed")
            return

        metadata = job_service.get(job_id)

        failed_files = metadata.get("failed_files", 0)

        if failed_files == metadata.get("total_files", 0):
            job_service.update_status(job_id, "failed")
        else:
            job_service.update_status(job_id, "completed")


batch_finalizer = BatchFinalizer()
