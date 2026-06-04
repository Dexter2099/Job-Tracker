from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models import ApplicationStatus


class JobApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1, max_length=120)
    role_title: str = Field(..., min_length=1, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    job_url: HttpUrl | None = None
    status: ApplicationStatus = ApplicationStatus.draft
    source: str | None = Field(default=None, max_length=120)
    contact_name: str | None = Field(default=None, max_length=160)
    contact_email: str | None = Field(default=None, max_length=255)
    salary_range: str | None = Field(default=None, max_length=120)
    notes: str | None = None
    follow_up_date: date | None = None
    applied_date: date | None = None


class JobApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=120)
    role_title: str | None = Field(default=None, min_length=1, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    job_url: HttpUrl | None = None
    status: ApplicationStatus | None = None
    source: str | None = Field(default=None, max_length=120)
    contact_name: str | None = Field(default=None, max_length=160)
    contact_email: str | None = Field(default=None, max_length=255)
    salary_range: str | None = Field(default=None, max_length=120)
    notes: str | None = None
    follow_up_date: date | None = None
    applied_date: date | None = None


class JobApplicationRead(BaseModel):
    id: int
    company: str
    role_title: str
    location: str | None
    job_url: str | None
    status: ApplicationStatus
    source: str | None
    contact_name: str | None
    contact_email: str | None
    salary_range: str | None
    notes: str | None
    follow_up_date: date | None
    applied_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatusHistoryRead(BaseModel):
    id: int
    application_id: int
    old_status: str | None
    new_status: str
    changed_at: datetime
    note: str | None

    model_config = ConfigDict(from_attributes=True)
