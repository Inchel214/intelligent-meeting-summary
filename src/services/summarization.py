from abc import ABC, abstractmethod
from ..models.meeting import Transcript, Summary


class Summarizer(ABC):
    @abstractmethod
    def generate(self, transcript: Transcript) -> Summary:
        pass


class QualityAssessor(ABC):
    @abstractmethod
    def assess_summary(self, summary: Summary, transcript: Transcript) -> float:
        pass

    @abstractmethod
    def assess_transcription(self, transcript: Transcript) -> float:
        pass
