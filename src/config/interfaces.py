from abc import ABC, abstractmethod
from typing import Any, Dict


class ConfigLoader(ABC):
    @abstractmethod
    def load(self, path: str) -> Dict[str, Any]:
        pass


class ConfigProvider(ABC):
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        pass

    @abstractmethod
    def all(self) -> Dict[str, Any]:
        pass
