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

    def to_images(
        self,
        file_data: bytes,
        image_format: str = "png",
        dpi: int = 150,
    ) -> list[tuple[str, bytes]]:
        """Rasterize every PDF page with Ghostscript.

        Returns ``[(filename, bytes), ...]`` sorted by page number.
        """
        device = "png16m" if image_format == "png" else "jpeg"
        extension = "png" if image_format == "png" else "jpg"
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "input.pdf"
            input_path.write_bytes(file_data)
            output_pattern = temp_path / "page-%03d." + extension
            command = [
                "gs",
                f"-sDEVICE={device}",
                "-dNOPAUSE",
                "-dQUIET",
                "-dBATCH",
                f"-r{dpi}",
                f"-sOutputFile={output_pattern}",
                str(input_path),
            ]
            try:
                subprocess.run(
                    command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=180,
                )
            except subprocess.TimeoutExpired as error:
                raise RuntimeError(
                    "PDF to image conversion timed out."
                ) from error
            except subprocess.CalledProcessError as error:
                error_message = (
                    error.stderr.decode(
                        errors="replace"
                    )
                )
                raise RuntimeError(
                    "Ghostscript failed to convert "
                    "the PDF: "
                    f"{error_message}"
                ) from error
            pages = sorted(
                temp_path.glob(
                    f"page-*.{extension}"
                )
            )
            if not pages:
                raise RuntimeError(
                    "Ghostscript did not produce "
                    "any page images."
                )
            return [
                (
                    page.name,
                    page.read_bytes(),
                )
                for page in pages
            ]


ghostscript_adapter = GhostscriptAdapter()
