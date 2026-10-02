import os

from app.ai.provider import AIProvider


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("AI_API_KEY")
        self.model = model or os.getenv("AI_MODEL", "gpt-4o-mini")

    def generate_review(self, payload: dict) -> dict:
        return {
            "summary": "AI review placeholder.",
            "issues": [],
            "explanation": "AI provider integration is ready but not yet connected to a live model.",
            "improvements": [],
            "optimized_code": payload.get("code", ""),
            "complexity_explanation": "Complexity analysis remains in the static analyzer layer.",
            "security_summary": "Security review pending provider validation.",
        }

    def generate_fix(self, payload: dict) -> dict:
        return {
            "fixed_code": payload.get("code", ""),
            "diff": [],
            "reason": "Provider abstraction is intentionally stubbed until a live provider is configured.",
        }
