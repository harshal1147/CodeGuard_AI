from app.ai.openai_provider import OpenAIProvider


class AIService:
    def __init__(self, provider: OpenAIProvider | None = None):
        self.provider = provider or OpenAIProvider()

    def review_code(self, payload: dict) -> dict:
        return self.provider.generate_review(payload)

    def fix_code(self, payload: dict) -> dict:
        return self.provider.generate_fix(payload)
