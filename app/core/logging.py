import logging
import re
import sys
import tempfile
from pathlib import Path

from app.core.config import settings

CATEGORY_PREFIXES: dict[str, tuple[str, ...]] = {
    "system": (),
    "activities": ("app.modules.jobs",),
    "background_remover": ("app.modules.background",),
    "compression": ("app.modules.compression",),
    "image_tools": ("app.modules.image",),
    "pdf_tools": ("app.modules.pdf",),
    "file_tools": ("app.modules.file_tools",),
    "devtools": ("app.modules.devtools",),
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


def _safe_log_name(tool_id: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "_", tool_id).strip("_").lower() or "unknown"


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


_file_formatter = logging.Formatter(
    fmt=(
        "%(asctime)s | %(levelname)-8s | %(name)s | "
        "%(funcName)s:%(lineno)d | %(message)s"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
)

_console_formatter = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_tool_loggers_configured: set[str] = set()


def _writable_log_dir() -> Path | None:
    for candidate in (Path("logs"), Path(tempfile.gettempdir()) / "logs"):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate
        except OSError:
            continue
    return None


def get_tool_logger(tool_id: str) -> logging.Logger:
    """Return a logger dedicated to a single tool.

    Writes to ``logs/<tool_id>.log`` in development and test environments.
    Records also propagate to the root logger so they surface on the
    console and in the catch-all ``system.log``.
    """
    safe_name = _safe_log_name(tool_id)
    logger = logging.getLogger(f"utils.tool.{safe_name}")
    if safe_name not in _tool_loggers_configured:
        _tool_loggers_configured.add(safe_name)
        if settings.app_env != "production":
            log_dir = _writable_log_dir()
            if log_dir is not None:
                try:
                    handler = logging.FileHandler(
                        log_dir / f"{safe_name}.log",
                        encoding="utf-8",
                    )
                    handler.setLevel(logging.DEBUG)
                    handler.setFormatter(_file_formatter)
                    logger.addHandler(handler)
                except OSError:
                    pass
    logger.propagate = True
    return logger


def setup_logging() -> None:
    console_handler = logging.StreamHandler(
        stream=sys.stdout,
    )
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(_console_formatter)

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
            file_handler.setFormatter(_file_formatter)
            file_handler.addFilter(CategoryFilter(category))
            root_logger.addHandler(file_handler)
        except OSError:
            continue
