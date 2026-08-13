from app.infrastructure.storage.local_storage import LocalStorage


class VercelStorage:
    def __init__(self) -> None:
        self._storage = LocalStorage()
