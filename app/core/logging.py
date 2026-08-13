import logging
import sys
import tempfile
from pathlib import Path

from app.core.config import settings


def _writable_log_dir() -> Path | None:
    for candidate in (Path("logs"), Path(tempfile.gettempdir()) / "logs"):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            continue
    return None


def setup_logging() -> None:
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(
        stream=sys.stdout,
    )
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    if settings.app_env == "production":
        return

    log_dir = _writable_log_dir()
    if log_dir is None:
        return

    try:
        file_handler = logging.FileHandler(
            log_dir / "app.log",
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except OSError:
        pass
