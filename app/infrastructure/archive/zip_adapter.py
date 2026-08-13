from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from app.shared.utils.file_util import is_safe_filename


class ZipAdapter:
    def create_archive(
        self,
        files: list[tuple[str, bytes]],
    ) -> bytes:
        archive_buffer = BytesIO()
        with ZipFile(
            archive_buffer,
            mode="w",
            compression=ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for filename, file_data in files:
                safe_name = Path(filename).name
                if not is_safe_filename(safe_name):
                    raise ValueError(
                        f"Invalid archive entry: {filename}"
                    )
                archive.writestr(
                    safe_name,
                    file_data,
                )
        return archive_buffer.getvalue()

    def create_archive_from_directory(
        self,
        source_directory: Path,
        output_path: Path,
    ) -> Path:
        source_directory = source_directory.resolve()
        with ZipFile(
            output_path,
            mode="w",
            compression=ZIP_DEFLATED,
            compresslevel=9,
        ) as archive:
            for file_path in sorted(
                source_directory.rglob("*")
            ):
                if not file_path.is_file():
                    continue
                real_path = file_path.resolve()
                if not str(real_path).startswith(
                    str(source_directory) + "/"
                ) and real_path != source_directory:
                    continue
                arcname = real_path.relative_to(
                    source_directory
                )
                archive.write(
                    real_path,
                    arcname=arcname.as_posix(),
                )
        return output_path


zip_adapter = ZipAdapter()
