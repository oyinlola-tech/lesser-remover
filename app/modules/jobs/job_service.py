import copy
from datetime import datetime, timezone

from app.core.logging import get_tool_logger
from app.infrastructure.jobs import local_job_storage


def _fmt_size(num_bytes: float) -> str:
    try:
        num_bytes = int(num_bytes)
    except (TypeError, ValueError):
        return "0 B"
    for unit in ("B", "KB", "MB", "GB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.0f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.0f} TB"


class JobService:
    def create(
        self,
        filenames: list[str],
        tool_id: str = "unknown",
    ) -> str:
        job_id = local_job_storage.create_job()
        files = []
        for index, filename in enumerate(filenames):
            files.append(
                {
                    "id": str(index),
                    "filename": filename,
                    "input_filename": "",
                    "status": "waiting",
                    "original_size_bytes": 0,
                    "compressed_size_bytes": 0,
                    "savings_percent": 0,

                    "output_filename": "",
                    "download_url": "",
                    "content_type": "",

                    "output_format": "",
                    "quality": None,
                    "compression_preset": "",
                    "width": None,
                    "height": None,

                    "target_size_bytes": None,
                    "target_achieved": False,

                    "error": None,
                }
            )
        metadata = local_job_storage.read_metadata(
            job_id
        )
        metadata.update(
            {
                "status": "created",
                "tool_id": tool_id,
                "total_files": len(files),
                "completed_files": 0,
                "failed_files": 0,
                "original_size_bytes": 0,
                "compressed_size_bytes": 0,
                "files": files,
                "download_url": None,
            }
        )
        local_job_storage.write_metadata(
            job_id,
            metadata,
        )

        tool_logger = get_tool_logger(tool_id)
        tool_logger.info(
            "Job created: job_id=%s, files=%d",
            job_id,
            len(files),
        )
        return job_id

    def set_input_filename(
        self,
        job_id: str,
        file_id: str,
        input_filename: str,
    ) -> None:
        metadata = (
            local_job_storage.read_metadata(
                job_id
            )
        )

        for file in metadata.get(
            "files",
            [],
        ):
            if file["id"] == file_id:
                file["input_filename"] = (
                    input_filename
                )
                break

        local_job_storage.write_metadata(
            job_id,
            metadata,
        )

    def update_status(
        self,
        job_id: str,
        status: str,
    ) -> None:
        metadata = local_job_storage.read_metadata(
            job_id
        )
        metadata["status"] = status
        metadata["updated_at"] = (
            datetime.now(timezone.utc).isoformat()
        )
        local_job_storage.write_metadata(
            job_id,
            metadata,
        )
        tool_id = metadata.get("tool_id", "unknown")
        get_tool_logger(tool_id).info(
            "Job %s status: %s", job_id, status
        )

    def update_file_status(
        self,
        job_id: str,
        file_id: str,
        status: str,
        original_size: int = 0,
        compressed_size: int = 0,
        savings_percent: float = 0,
        error: str | None = None,
        output_filename: str = "",
        download_url: str = "",
        content_type: str = "",
        output_format: str = "",
        quality: int | None = None,
        compression_preset: str = "",
        width: int | None = None,
        height: int | None = None,
        target_size_bytes: int | None = None,
        target_achieved: bool = False,
    ) -> None:
        metadata = local_job_storage.read_metadata(
            job_id
        )
        tool_id = metadata.get("tool_id", "unknown")
        tool_logger = get_tool_logger(tool_id)
        for file in metadata.get("files", []):
            if file["id"] == file_id:
                previous_status = file["status"]
                file["status"] = status
                file["original_size_bytes"] = original_size
                file["compressed_size_bytes"] = compressed_size
                file["savings_percent"] = savings_percent
                file["error"] = error
                file["output_filename"] = output_filename
                file["download_url"] = download_url
                file["content_type"] = content_type
                file["output_format"] = output_format
                file["quality"] = quality
                file["compression_preset"] = compression_preset

                file["width"] = width
                file["height"] = height

                file["target_size_bytes"] = target_size_bytes
                file["target_achieved"] = target_achieved

                if status == "completed":
                    tool_logger.info(
                        "File %s completed for job %s: %s -> %s (%s%% saved)",
                        file.get("filename", file_id),
                        job_id,
                        _fmt_size(original_size),
                        _fmt_size(compressed_size),
                        savings_percent,
                    )
                if status == "failed":
                    tool_logger.warning(
                        "File %s failed for job %s: %s",
                        file.get("filename", file_id),
                        job_id,
                        error or "no error reason",
                    )
                if (
                    status == "completed"
                    and previous_status != "completed"
                ):
                    metadata["completed_files"] += 1
                if (
                    status == "failed"
                    and previous_status != "failed"
                ):
                    metadata["failed_files"] += 1
                break
        metadata["original_size_bytes"] = sum(
            item.get("original_size_bytes", 0)
            for item in metadata.get("files", [])
        )
        metadata["compressed_size_bytes"] = sum(
            item.get("compressed_size_bytes", 0)
            for item in metadata.get("files", [])
        )
        local_job_storage.write_metadata(
            job_id,
            metadata,
        )

    def set_download_url(
        self,
        job_id: str,
        download_url: str,
    ) -> None:
        metadata = local_job_storage.read_metadata(
            job_id
        )
        metadata["download_url"] = download_url
        local_job_storage.write_metadata(
            job_id,
            metadata,
        )
        tool_id = metadata.get("tool_id", "unknown")
        get_tool_logger(tool_id).info(
            "Download ready for job %s", job_id
        )

    def get(self, job_id: str) -> dict:
        metadata = local_job_storage.read_metadata(job_id)
        return copy.deepcopy(metadata)

    def delete(self, job_id: str) -> None:
        local_job_storage.delete_job(job_id)

    def cancel(self, job_id: str) -> None:
        metadata = local_job_storage.read_metadata(
            job_id
        )
        if not metadata:
            raise ValueError("Job not found.")
        if metadata.get("status") in {
            "completed",
            "failed",
            "cancelled",
        }:
            return
        self.update_status(job_id, "cancelled")
        tool_id = metadata.get("tool_id", "unknown")
        get_tool_logger(tool_id).info(
            "Job %s cancelled", job_id
        )

    def is_cancelled(self, job_id: str) -> bool:
        metadata = local_job_storage.read_metadata(
            job_id
        )
        return metadata.get("status") == "cancelled"


job_service = JobService()
