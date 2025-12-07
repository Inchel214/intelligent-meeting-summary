from abc import ABC, abstractmethod
from typing import Optional
from ..models.meeting import Transcript


class TranscriptionService(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Transcript:
        pass


class SpeakerDiarization(ABC):
    @abstractmethod
    def assign_speakers(self, transcript: Transcript) -> Transcript:
        pass
