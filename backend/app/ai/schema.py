from pydantic import BaseModel, Field


class AIReviewSchema(BaseModel):
    summary: str
    issues: list[dict] = Field(default_factory=list)
    explanation: str
    improvements: list[str] = Field(default_factory=list)
    optimized_code: str
    complexity_explanation: str
    security_summary: str
