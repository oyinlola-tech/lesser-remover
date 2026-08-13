from abc import ABC, abstractmethod
from pathlib import Path


class StorageInterface(ABC):
    @abstractmethod
    def save(self, source_path: Path, destination_path: Path) -> Path:
        pass

    @abstractmethod
    def delete(self, file_path: Path) -> None:
        pass

    @abstractmethod
    def exists(self, file_path: Path) -> bool:
        pass

    @abstractmethod
    def get_size(self, file_path: Path) -> int:
        pass
