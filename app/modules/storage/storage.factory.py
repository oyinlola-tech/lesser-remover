from typing import Protocol


class StorageInterface(Protocol):
    def save(self, source, destination):
        ...

    def delete(self, file_path):
        ...

    def exists(self, file_path) -> bool:
        ...

    def get_size(self, file_path) -> int:
        ...


class StorageFactory:
    @staticmethod
    def create(storage_type: str):
        if storage_type == "local":
            from app.infrastructure.storage.local_storage import storage
            return storage
        raise ValueError(f"Unsupported storage type: {storage_type}")


class StorageTypes:
    LOCAL = "local"
    VERCEL = "vercel"
