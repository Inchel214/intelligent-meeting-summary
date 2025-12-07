from abc import ABC, abstractmethod
from typing import Dict


class AIServiceAdapter(ABC):
    @abstractmethod
    def generate_summary(self, transcript_text: str, prompt: str) -> Dict:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_model_info(self) -> Dict:
        pass
