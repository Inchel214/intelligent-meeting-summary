class MeetingError(Exception):
    pass


class TranscriptionError(MeetingError):
    pass


class SummarizationError(MeetingError):
    pass
