from abc import ABC, abstractmethod
from typing import Any, Optional


class ObjectStorage(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes, content_type: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def load(self, key: str) -> bytes:
        pass


class MetadataRepository(ABC):
    @abstractmethod
    def save_metadata(self, key: str, metadata: Any) -> None:
        pass

    @abstractmethod
    def get_metadata(self, key: str) -> Optional[Any]:
        pass
