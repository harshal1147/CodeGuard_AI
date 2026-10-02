from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def generate_review(self, payload: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def generate_fix(self, payload: dict) -> dict:
        raise NotImplementedError
