from abc import ABC, abstractmethod


class TestCaseAdapter(ABC):
    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def teardown(self) -> None:
        pass
