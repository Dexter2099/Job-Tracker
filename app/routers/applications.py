from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ApplicationStatus, JobApplication, StatusHistory
from app.schemas import JobApplicationCreate, JobApplicationRead, JobApplicationUpdate


router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[JobApplicationRead])
def list_applications(
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    company: str | None = None,
    role: str | None = None,
    applied_date_from: date | None = None,
    applied_date_to: date | None = None,
    follow_up_date_from: date | None = None,
    follow_up_date_to: date | None = None,
    follow_up_before: date | None = None,
    sort: Literal[
        "applied_date_desc",
        "applied_date_asc",
        "follow_up_date_desc",
        "follow_up_date_asc",
        "created_at_desc",
        "created_at_asc",
    ] = "created_at_desc",
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[JobApplication]:
    query = select(JobApplication)

    if status_filter is not None:
        query = query.where(JobApplication.status == status_filter)

    if company is not None:
        query = query.where(JobApplication.company.ilike(f"%{company}%"))

    if role is not None:
        query = query.where(JobApplication.role_title.ilike(f"%{role}%"))

    if applied_date_from is not None:
        query = query.where(JobApplication.applied_date >= applied_date_from)

    if applied_date_to is not None:
        query = query.where(JobApplication.applied_date <= applied_date_to)

    if follow_up_date_from is not None:
        query = query.where(JobApplication.follow_up_date >= follow_up_date_from)

    if follow_up_date_to is not None:
        query = query.where(JobApplication.follow_up_date <= follow_up_date_to)

    if follow_up_before is not None:
        query = query.where(JobApplication.follow_up_date <= follow_up_before)

    sort_options = {
        "applied_date_desc": (
            JobApplication.applied_date.desc(),
            JobApplication.id.desc(),
        ),
        "applied_date_asc": (JobApplication.applied_date.asc(), JobApplication.id.asc()),
        "follow_up_date_desc": (
            JobApplication.follow_up_date.desc(),
            JobApplication.id.desc(),
        ),
        "follow_up_date_asc": (
            JobApplication.follow_up_date.asc(),
            JobApplication.id.asc(),
        ),
        "created_at_desc": (
            JobApplication.created_at.desc(),
            JobApplication.id.desc(),
        ),
        "created_at_asc": (JobApplication.created_at.asc(), JobApplication.id.asc()),
    }
    query = query.order_by(*sort_options[sort])

    return db.execute(query.offset(offset).limit(limit)).scalars().all()


@router.post("", response_model=JobApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(
    application: JobApplicationCreate,
    db: Session = Depends(get_db),
) -> JobApplication:
    application_data = application.model_dump()
    if application_data["job_url"] is not None:
        application_data["job_url"] = str(application_data["job_url"])

    db_application = JobApplication(**application_data)
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.get("/{application_id}", response_model=JobApplicationRead)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
) -> JobApplication:
    application = db.get(JobApplication, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return application


@router.patch("/{application_id}", response_model=JobApplicationRead)
def update_application(
    application_id: int,
    application_update: JobApplicationUpdate,
    db: Session = Depends(get_db),
) -> JobApplication:
    application = db.get(JobApplication, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    update_data = application_update.model_dump(exclude_unset=True)
    if update_data.get("job_url") is not None:
        update_data["job_url"] = str(update_data["job_url"])

    old_status = application.status
    new_status = update_data.get("status")

    for field, value in update_data.items():
        setattr(application, field, value)

    if new_status is not None and new_status != old_status:
        db.add(
            StatusHistory(
                application_id=application.id,
                old_status=old_status,
                new_status=new_status,
                note=update_data.get("notes"),
            )
        )

    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
) -> None:
    application = db.get(JobApplication, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    db.delete(application)
    db.commit()
