"""Per-file processing for batch compression jobs."""

import logging
from pathlib import Path

from app.modules.compression.batch_compression.batch_file_compressor import (
    batch_file_compressor,
)
from app.modules.compression.batch_compression.batch_output_writer import (
    batch_output_writer,
)
from app.modules.jobs.job_service import (
    job_service,
)
from app.shared.file_inspection.file_validation import (
    inspect_and_validate,
)

logger = logging.getLogger(__name__)


class BatchFileProcessor:

    def process_file(
        self,
        job_id: str,
        file_info: dict,
        job_input_directory: Path,
        output_directory: Path,
        image_output_format: str,
        compression_preset: str,
        max_dimension: int | None = None,
        target_size_kb: int | None = None,
        strip_metadata: bool = True,
        quality: int | None = None,
    ) -> None:

        file_id = file_info["id"]
        original_filename = file_info["filename"]
        input_filename = file_info["input_filename"]

        logger.info(
            "Processing file %s (id=%s) for job %s",
            original_filename,
            file_id,
            job_id,
        )

        job_service.update_file_status(
            job_id,
            file_id,
            "processing",
        )

        try:
            input_path = job_input_directory / input_filename

            if not input_path.exists():
                raise FileNotFoundError(
                    f"Input file not found: {original_filename}"
                )

            file_data = input_path.read_bytes()

            inspection = inspect_and_validate(file_data)

            original_size = len(file_data)

            target_size_bytes = None
            if target_size_kb:
                target_size_bytes = target_size_kb * 1024

            result = batch_file_compressor.compress_file(
                file_data=file_data,
                inspection=inspection,
                image_output_format=image_output_format,
                compression_preset=compression_preset,
                target_size_bytes=target_size_bytes,
                max_dimension=max_dimension,
                strip_metadata=strip_metadata,
                quality=quality,
            )

            status_kwargs = batch_output_writer.write_output(
                result=result,
                file_data=file_data,
                original_size=original_size,
                original_filename=original_filename,
                inspection=inspection,
                output_directory=output_directory,
                target_size_bytes=target_size_bytes,
            )

            logger.info(
                "Completed file %s (id=%s) for job %s: %s -> %s bytes, saved %.2f%%",
                original_filename,
                file_id,
                job_id,
                status_kwargs["original_size"],
                status_kwargs["compressed_size"],
                status_kwargs["savings_percent"],
            )

            job_service.update_file_status(
                job_id,
                file_id,
                "completed",
                **status_kwargs,
            )

        except Exception as error:

            logger.exception(
                "Failed to process file %s (id=%s) for job %s: %s",
                original_filename,
                file_id,
                job_id,
                error,
            )

            job_service.update_file_status(
                job_id,
                file_id,
                "failed",
                error=str(error),
            )


batch_file_processor = BatchFileProcessor()
