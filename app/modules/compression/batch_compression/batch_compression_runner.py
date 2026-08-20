"""Background runner orchestrating per-file processing for batch jobs."""

import logging

from app.infrastructure.jobs import local_job_storage
from app.modules.compression.batch_compression.batch_file_processor import (
    batch_file_processor,
)
from app.modules.compression.batch_compression.batch_finalizer import (
    batch_finalizer,
)
from app.modules.jobs.job_service import (
    job_service,
)

logger = logging.getLogger(__name__)


class BatchCompressionRunner:

    def process(
        self,
        job_id: str,
        files: list[dict],
        image_output_format: str,
        compression_preset: str,
        max_dimension: int | None = None,
        target_size_kb: int | None = None,
        strip_metadata: bool = True,
        quality: int | None = None,
    ) -> None:

        job_service.update_status(job_id, "processing")

        job_input_directory = local_job_storage.get_input_path(job_id)

        output_directory = local_job_storage.get_output_path(job_id)

        output_directory.mkdir(parents=True, exist_ok=True)

        for file_info in files:

            if job_service.is_cancelled(job_id):
                logger.info(
                    "Job %s cancelled, stopping processing",
                    job_id,
                )
                return

            batch_file_processor.process_file(
                job_id=job_id,
                file_info=file_info,
                job_input_directory=job_input_directory,
                output_directory=output_directory,
                image_output_format=image_output_format,
                compression_preset=compression_preset,
                max_dimension=max_dimension,
                target_size_kb=target_size_kb,
                strip_metadata=strip_metadata,
                quality=quality,
            )

        batch_finalizer.finalize_job(job_id)

    def finalize(
        self,
        job_id: str,
    ) -> None:
        batch_finalizer.finalize_job(job_id)


batch_compression_runner = BatchCompressionRunner()
