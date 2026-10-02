from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisCreate(BaseModel):
    project_id: str
    language: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)
    code: str = Field(..., max_length=5242880)
    source: str = "paste"


class AnalysisResponse(BaseModel):
    id: str
    project_id: str
    language: str
    status: str = "pending"
    score: int | None = None
    findings_count: int = 0
    result: dict | None = None
    created_at: datetime | None = None
