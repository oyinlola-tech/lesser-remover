import logging
import sys
import tempfile
from pathlib import Path

from app.core.config import settings

CATEGORY_PREFIXES: dict[str, tuple[str, ...]] = {
    "system": (),
    "activities": ("app.modules.jobs",),
    "background_remover": ("app.modules.background",),
    "compression": ("app.modules.compression",),
}

SPECIFIC_PREFIXES = tuple(
    prefix
    for category, prefixes in CATEGORY_PREFIXES.items()
    if category != "system"
    for prefix in prefixes
)


def _matches_any(name: str, prefixes: tuple[str, ...]) -> bool:
    return any(
        name == prefix or name.startswith(prefix + ".")
        for prefix in prefixes
    )


class CategoryFilter(logging.Filter):
    """Routes log records to the file handler of their category.

    Records are classified by the logger name prefix:
    - ``background_remover``  -> app.modules.background.*
    - ``compression``         -> app.modules.compression.*
    - ``activities``          -> app.modules.jobs.*
    - ``system``              -> everything else (core, infrastructure,
                                 storage, uvicorn, root, ...)
    """

    def __init__(self, category: str) -> None:
        super().__init__()
        self.category = category

    def filter(self, record: logging.LogRecord) -> bool:
        if self.category == "system":
            return not _matches_any(record.name, SPECIFIC_PREFIXES)
        return _matches_any(record.name, CATEGORY_PREFIXES[self.category])


def _writable_log_dir() -> Path | None:
    for candidate in (Path("logs"), Path(tempfile.gettempdir()) / "logs"):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            continue
    return None


def setup_logging() -> None:
    console_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)-8s | %(name)s | "
            "%(funcName)s:%(lineno)d | %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(
        stream=sys.stdout,
    )
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    if settings.app_env == "production":
        return

    log_dir = _writable_log_dir()
    if log_dir is None:
        return

    for category in CATEGORY_PREFIXES:
        try:
            file_handler = logging.FileHandler(
                log_dir / f"{category}.log",
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            file_handler.addFilter(CategoryFilter(category))
            root_logger.addHandler(file_handler)
        except OSError:
            continue