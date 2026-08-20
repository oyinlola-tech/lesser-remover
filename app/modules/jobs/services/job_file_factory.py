"""Job metadata file-entry factory."""


def fmt_size(num_bytes: float) -> str:
    try:
        num_bytes = int(num_bytes)
    except (TypeError, ValueError):
        return "0 B"
    for unit in ("B", "KB", "MB", "GB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.0f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.0f} TB"


def build_file_entry(index: int, filename: str) -> dict:
    return {
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
