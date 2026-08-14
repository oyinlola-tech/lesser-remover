"""Storage adapter contract.

Business logic depends on this interface only, never on the local
filesystem or Vercel Blob directly. Adapters are selected through
``STORAGE_DRIVER`` in configuration.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class StorageInterface(ABC):
    """Contract implemented by LocalStorage and VercelStorage."""

    upload_path: Path
    processed_path: Path
    compressed_path: Path
    temp_path: Path

    @abstractmethod
    def save(
        self,
        source_path: Path,
        destination_path: Path,
    ) -> Path:
        """Move or upload a source file to the destination path."""

    @abstractmethod
    def write(self, file_path: Path, data: bytes) -> None:
        """Persist raw bytes at the given path."""

    @abstractmethod
    def read(self, file_path: Path) -> bytes:
        """Read raw bytes from the given path."""

    @abstractmethod
    def materialize(self, file_path: Path) -> Path:
        """Ensure the file is locally readable and return its local path."""

    @abstractmethod
    def delete(self, file_path: Path) -> None:
        """Delete the file if it exists. Must be idempotent."""

    @abstractmethod
    def exists(self, file_path: Path) -> bool:
        """Return whether the file exists."""

    @abstractmethod
    def get_size(self, file_path: Path) -> int:
        """Return the file size in bytes."""

    @abstractmethod
    def get_url(self, file_path: Path) -> str:
        """Return a public URL for the file, or empty string if none."""
