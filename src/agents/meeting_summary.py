from abc import ABC, abstractmethod
from typing import Dict, Any
from ..models.meeting import MeetingInput, Transcript, Summary


class MeetingSummaryAgent(ABC):
    @abstractmethod
    def transcribe(self, input_data: MeetingInput) -> Transcript:
        pass

    @abstractmethod
    def summarize(self, transcript: Transcript) -> Summary:
        pass

    @abstractmethod
    def process(self, input_data: MeetingInput) -> Dict[str, Any]:
        pass
