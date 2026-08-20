"""Lazy PyMuPDF import for the ghostscript adapter."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pymupdf


def get_pymupdf() -> "pymupdf":
    """Import PyMuPDF lazily so the app boots when it is not installed.

    The module is imported on first use rather than at startup so the
    rest of the API stays available (and PDF tools report themselves as
    unavailable) on runtimes such as Vercel that cannot install it.
    """
    try:
        import pymupdf
    except ImportError as error:
        raise RuntimeError(
            "PyMuPDF is required for PDF compression and "
            "PDF-to-image conversion but is not installed."
        ) from error
    return pymupdf
