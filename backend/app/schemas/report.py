from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: str
    analysis_id: str
    title: str
    payload: dict
