from abc import ABC, abstractmethod


class AudioExtractor(ABC):
    @abstractmethod
    def extract(self, source_path: str) -> str:
        pass


class AudioValidator(ABC):
    @abstractmethod
    def validate(self, audio_path: str) -> bool:
        pass


class AudioConverter(ABC):
    @abstractmethod
    def convert(self, audio_path: str, target_format: str) -> str:
        pass
