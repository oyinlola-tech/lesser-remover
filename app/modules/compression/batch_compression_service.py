from pathlib import Path

from app.core.config import settings
from app.modules.archive.archive_service import (
    archive_service,
)
from app.modules.compression.compression_repository import (
    compression_repository,
)
from app.modules.compression.compression_service import (
    compression_service,
)
from app.modules.jobs.job_service import (
    job_service,
)
from app.infrastructure.jobs.local_job_storage import (
    local_job_storage,
)
from app.shared.file_inspection.file_validation import (
    inspect_and_validate,
)
from app.shared.utils.file_util import (
    generate_filename,
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
    ) -> None:
        job_service.update_status(
            job_id,
            "processing",
        )

        job_input_directory = (
            local_job_storage
            .get_input_path(job_id)
        )

        output_directory = (
            local_job_storage
            .get_output_path(job_id)
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        for file_info in files:

            if job_service.is_cancelled(
                job_id
            ):
                return

            file_id = file_info["id"]

            original_filename = (
                file_info["filename"]
            )

            input_filename = (
                file_info["input_filename"]
            )

            job_service.update_file_status(
                job_id,
                file_id,
                "processing",
            )

            try:

                input_path = (
                    job_input_directory
                    / input_filename
                )

                if not input_path.exists():
                    raise FileNotFoundError(
                        f"Input file not found: "
                        f"{original_filename}"
                    )

                file_data = (
                    input_path.read_bytes()
                )

                inspection = (
                    inspect_and_validate(
                        file_data
                    )
                )

                original_size = len(
                    file_data
                )

                target_size_bytes = None
                if target_size_kb:
                    target_size_bytes = target_size_kb * 1024

                if (
                    inspection.category.value
                    == "image"
                ):

                    (
                        compressed_data,
                        content_type,
                        actual_quality,
                        width,
                        height,
                    ) = (
                        compression_service
                        .compress_image(
                            file_data=file_data,
                            preset=compression_preset,
                            output_format=(
                                image_output_format
                            ),
                            max_dimension=max_dimension,
                            target_size_bytes=target_size_bytes,
                        )
                    )

                    extension = {
                        "webp": "webp",
                        "jpeg": "jpg",
                        "png": "png",
                    }[
                        image_output_format
                    ]

                elif (
                    inspection.category.value
                    == "pdf"
                ):

                    (
                        compressed_data,
                        content_type,
                        _pdf_quality,
                    ) = (
                        compression_service
                        .compress_pdf(
                            file_data=file_data,
                            preset=compression_preset,
                        )
                    )

                    # actual preset/quality chosen for PDF
                    actual_pdf_preset = _pdf_quality

                    extension = "pdf"

                else:

                    raise ValueError(
                        "Unsupported file type."
                    )

                compressed_size = len(
                    compressed_data
                )

                if (
                    compressed_size
                    >= original_size
                ):
                    compressed_data = file_data

                    compressed_size = (
                        original_size
                    )

                    extension = (
                        Path(
                            original_filename
                        )
                        .suffix
                        .lower()
                        .lstrip(".")
                    )

                    content_type = (
                        inspection.mime_type
                    )

                output_filename = (
                    generate_filename(
                        original_filename,
                        extension=extension,
                    )
                )

                output_path = (
                    output_directory
                    / output_filename
                )

                output_path.write_bytes(
                    compressed_data
                )

                savings_percent = (
                    (
                        1 - (
                            compressed_size /
                            original_size
                        )
                    ) * 100
                )

                target_achieved = (
                    target_size_bytes is not None
                    and compressed_size <= target_size_bytes
                )

                job_service.update_file_status(
                    job_id,
                    file_id,
                    "completed",
                    original_size=(
                        original_size
                    ),
                    compressed_size=(
                        compressed_size
                    ),
                    savings_percent=round(
                        savings_percent,
                        2,
                    ),
                    output_filename=(
                        output_path.name
                    ),
                    download_url=(
                        "/api/compression/"
                        "download/"
                        f"{output_path.name}"
                    ),
                    content_type=(
                        content_type
                    ),
                    output_format=extension,
                    quality=actual_quality if 'actual_quality' in locals() else None,
                    compression_preset=(
                        actual_pdf_preset
                        if 'actual_pdf_preset' in locals()
                        else compression_preset
                    ),
                    width=width if 'width' in locals() else None,
                    height=height if 'height' in locals() else None,
                    target_size_bytes=target_size_bytes,
                    target_achieved=target_achieved,
                )

            except Exception as error:

                job_service.update_file_status(
                    job_id,
                    file_id,
                    "failed",
                    error=str(error),
                )

        self._finalize_job(
            job_id
        )

    def _finalize_job(
        self,
        job_id: str,
    ) -> None:

        if job_service.is_cancelled(
            job_id
        ):
            return

        metadata = job_service.get(
            job_id
        )

        output_directory = (
            local_job_storage
            .get_output_path(job_id)
        )

        output_files = [
            path
            for path in output_directory.iterdir()
            if path.is_file()
        ]

        if not output_files:
            job_service.update_status(
                job_id,
                "failed",
            )

            return

        zip_filename = (
            f"compressed_{job_id}.zip"
        )

        zip_path = (
            local_job_storage
            .get_job_path(job_id)
            / zip_filename
        )

        archive_service.create_zip_from_directory(
            output_directory,
            zip_path,
        )

        download_path = (
            local_job_storage.move_download(
                zip_path,
                zip_filename,
            )
        )

        job_service.set_download_url(
            job_id,
            (
                "/api/compression/"
                "download/"
                f"{download_path.name}"
            ),
        )

        metadata = job_service.get(
            job_id
        )

        failed_files = metadata.get(
            "failed_files",
            0,
        )

        if failed_files == metadata.get(
            "total_files",
            0,
        ):
            job_service.update_status(
                job_id,
                "failed",
            )

        else:
            job_service.update_status(
                job_id,
                "completed",
            )


batch_compression_service = BatchCompressionService()
