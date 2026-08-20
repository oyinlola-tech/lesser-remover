"""Persist a compressed file and compute its result metadata."""

from pathlib import Path

from app.modules.compression.batch_compression.batch_file_compressor import (
    CompressionResult,
)
from app.modules.compression.compression_repository import (
    compression_repository,
)
from app.shared.utils.file_util import (
    generate_filename,
)


class BatchOutputWriter:

    def write_output(
        self,
        result: CompressionResult,
        file_data: bytes,
        original_size: int,
        original_filename: str,
        inspection,
        output_directory: Path,
        target_size_bytes: int | None,
    ) -> dict:
        """Write the compressed file and return job status update kwargs."""

        compressed_size = len(result.data)

        if compressed_size >= original_size:
            result.data = file_data
            compressed_size = original_size
            result.extension = (
                Path(original_filename).suffix.lower().lstrip(".")
            )
            result.content_type = inspection.mime_type

        output_filename = generate_filename(
            original_filename,
            extension=result.extension,
        )

        output_path = output_directory / output_filename

        output_path.write_bytes(result.data)

        compression_repository.save(result.data, output_filename)

        savings_percent = (
            (1 - (compressed_size / original_size)) * 100
            if original_size > 0
            else 0.0
        )

        target_achieved = (
            target_size_bytes is not None
            and compressed_size <= target_size_bytes
        )

        return {
            "output_filename": output_path.name,
            "download_url": (
                "/api/v1/compression/download/"
                f"{output_path.name}"
            ),
            "content_type": result.content_type,
            "output_format": result.extension,
            "quality": result.quality,
            "compression_preset": result.compression_preset,
            "width": result.width,
            "height": result.height,
            "target_size_bytes": target_size_bytes,
            "target_achieved": target_achieved,
            "savings_percent": round(savings_percent, 2),
            "original_size": original_size,
            "compressed_size": compressed_size,
        }


batch_output_writer = BatchOutputWriter()
