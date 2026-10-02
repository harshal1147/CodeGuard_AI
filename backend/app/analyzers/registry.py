from app.analyzers.base import Analyzer


class AnalyzerRegistry:
    def __init__(self):
        self._analyzers: dict[str, Analyzer] = {}

    def register(self, name: str, analyzer: Analyzer) -> None:
        self._analyzers[name] = analyzer

    def get(self, name: str) -> Analyzer | None:
        return self._analyzers.get(name)

    def list_names(self) -> list[str]:
        return list(self._analyzers.keys())
