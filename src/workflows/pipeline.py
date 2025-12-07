from abc import ABC, abstractmethod
from ..models.meeting import MeetingInput, Transcript, Summary


class ProcessingPipeline(ABC):
    @abstractmethod
    def run(self, input_data: MeetingInput) -> Summary:
        pass

    @abstractmethod
    def transcribe(self, input_data: MeetingInput) -> Transcript:
        pass

    @abstractmethod
    def summarize(self, transcript: Transcript) -> Summary:
        pass
