import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


class GhostscriptAdapter:

    QUALITY_SETTINGS = {
        "screen": "/screen",
        "ebook": "/ebook",
        "printer": "/printer",
        "prepress": "/prepress",
        "default": "/default",
    }

    def compress(
        self,
        file_data: bytes,
        quality: str = "ebook",
    ) -> bytes:
        if quality not in self.QUALITY_SETTINGS:
            raise ValueError(
                f"Unsupported PDF quality: {quality}"
            )
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "input.pdf"
            output_path = temp_path / "output.pdf"
            input_path.write_bytes(file_data)
            command = [
                "gs",
                "-sDEVICE=pdfwrite",
                "-dCompatibilityLevel=1.4",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-dPDFSETTINGS="
                f"{self.QUALITY_SETTINGS[quality]}",
                "-sOutputFile="
                f"{output_path}",
                str(input_path),
            ]
            try:
                subprocess.run(
                    command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=120,
                )
            except subprocess.TimeoutExpired as error:
                raise RuntimeError(
                    "PDF compression timed out."
                ) from error
            except subprocess.CalledProcessError as error:
                error_message = (
                    error.stderr.decode(
                        errors="replace"
                    )
                )
                raise RuntimeError(
                    "Ghostscript failed to "
                    "compress the PDF: "
                    f"{error_message}"
                ) from error
            if not output_path.exists():
                raise RuntimeError(
                    "Ghostscript did not produce "
                    "an output PDF."
                )
            return output_path.read_bytes()


ghostscript_adapter = GhostscriptAdapter()
