from __future__ import annotations

from typing import TYPE_CHECKING
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.ai_review import AIReview
    from app.models.file import File
    from app.models.issue import Issue
    from app.models.project import Project
    from app.models.report import Report


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    file_id: Mapped[str | None] = mapped_column(ForeignKey("files.id"), nullable=True)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    findings_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="analyses")
    file: Mapped["File"] = relationship(back_populates="analyses")
    issues: Mapped[list["Issue"]] = relationship(back_populates="analysis")
    ai_review: Mapped["AIReview"] = relationship(back_populates="analysis")
    reports: Mapped[list["Report"]] = relationship(back_populates="analysis")
