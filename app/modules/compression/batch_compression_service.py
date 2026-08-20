"""Facade over the batch compression runner."""

from app.modules.compression.batch_compression.batch_compression_runner import (
    batch_compression_runner,
)


class BatchCompressionService:

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
        return batch_compression_runner.process(
            job_id,
            files,
            image_output_format,
            compression_preset,
            max_dimension,
            target_size_kb,
            strip_metadata,
            quality,
        )

    def _finalize_job(
        self,
        job_id: str,
    ) -> None:
        return batch_compression_runner.finalize(job_id)


batch_compression_service = BatchCompressionService()
