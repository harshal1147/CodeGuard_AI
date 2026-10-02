class Analyzer:
    """Base interface for language-specific analyzers."""

    name = "base"

    def detect_language(self, code: str, filename: str | None = None) -> str:
        return "unknown"

    def analyze(self, code: str, metadata: dict | None = None) -> dict:
        return {"issues": [], "metrics": {}}
