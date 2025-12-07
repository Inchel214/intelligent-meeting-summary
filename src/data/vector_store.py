from abc import ABC, abstractmethod
from typing import List, Optional, Sequence


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, items: Sequence[str], namespace: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def query(self, text: str, top_k: int = 5, namespace: Optional[str] = None) -> List[str]:
        pass
