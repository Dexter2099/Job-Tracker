from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Date, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ApplicationStatus(StrEnum):
    draft = "draft"
    applied = "applied"
    screening = "screening"
    interview = "interview"
    technical_interview = "technical_interview"
    offer = "offer"
    rejected = "rejected"
    withdrawn = "withdrawn"


class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    role_title: Mapped[str] = mapped_column(String(160), nullable=False)
    location: Mapped[str | None] = mapped_column(String(160), nullable=True)
    job_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name="application_status"),
        nullable=False,
        default=ApplicationStatus.draft,
        index=True,
    )
    source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    salary_range: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    applied_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
