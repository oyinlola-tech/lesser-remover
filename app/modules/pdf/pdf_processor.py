from pathlib import Path


class PdfProcessor:
    def process(self, file_path: Path) -> bytes:
        return file_path.read_bytes()
