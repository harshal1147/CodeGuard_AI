from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AIReview(Base):
    __tablename__ = "ai_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id"), nullable=False, unique=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    issues: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    improvements: Mapped[list | None] = mapped_column(JSON, nullable=True)
    optimized_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    complexity_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    security_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    analysis: Mapped["Analysis"] = relationship(back_populates="ai_review")
