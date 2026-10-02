from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id: Mapped[str] = mapped_column(ForeignKey("analyses.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    line: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    analysis: Mapped["Analysis"] = relationship(back_populates="issues")
