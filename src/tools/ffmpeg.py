from abc import ABC, abstractmethod


class FfmpegTool(ABC):
    @abstractmethod
    def extract_audio(self, video_path: str) -> str:
        pass

    @abstractmethod
    def convert(self, input_path: str, output_path: str, codec: str) -> str:
        pass
