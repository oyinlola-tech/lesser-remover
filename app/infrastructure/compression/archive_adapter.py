import subprocess
from pathlib import Path


class ArchiveAdapter:
    def compress(
        self,
        source_path: Path,
        destination_path: Path,
    ) -> Path:
        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        try:
            subprocess.run(
                [
                    "zip",
                    "-j",
                    str(destination_path),
                    str(source_path),
                ],
                check=True,
                capture_output=True,
                timeout=120,
            )
        except subprocess.CalledProcessError as error:
            detail = (
                error.stderr.decode("utf-8", errors="replace")
                if error.stderr
                else str(error)
            )
            raise RuntimeError(
                f"zip failed: {detail}"
            ) from error
        except FileNotFoundError as error:
            raise RuntimeError(
                "zip command not found. "
                "Please install zip."
            ) from error
        return destination_path


archive_adapter = ArchiveAdapter()
