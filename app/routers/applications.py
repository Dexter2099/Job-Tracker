import csv
from datetime import date
from io import StringIO
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    ApplicationStatus,
    ApplicationStatusHistory,
    Company,
    Contact,
    FollowUpReminder,
    JobApplication,
)
from app.schemas import (
    FollowUpReminderCreate,
    FollowUpReminderRead,
    FollowUpReminderUpdate,
    JobApplicationCreate,
    JobApplicationRead,
    JobApplicationUpdate,
    StatusHistoryRead,
)


router = APIRouter(prefix="/applications", tags=["applications"])

CSV_EXPORT_COLUMNS = [
    "id",
    "company",
    "role_title",
    "location",
    "status",
    "applied_date",
    "follow_up_date",
    "contact_name",
    "contact_email",
    "notes",
    "created_at",
    "updated_at",
]


def get_or_create_company(db: Session, name: str) -> Company:
    company = db.execute(select(Company).where(Company.name == name)).scalar_one_or_none()
    if company is not None:
        return company

    company = Company(name=name)
    db.add(company)
    db.flush()
    return company


def get_or_create_contact(
    db: Session,
    company_id: int,
    name: str,
    email: str | None,
) -> Contact:
    query = select(Contact).where(Contact.company_id == company_id)
    if email is not None:
        query = query.where(Contact.email == email)
    else:
        query = query.where(Contact.name == name, Contact.email.is_(None))

    contact = db.execute(query).scalar_one_or_none()
    if contact is not None:
        return contact

    contact = Contact(company_id=company_id, name=name, email=email)
    db.add(contact)
    db.flush()
    return contact


def apply_application_export_filters(
    query,
    status_filter: ApplicationStatus | None,
    company: str | None,
    role: str | None,
    follow_up_before: date | None,
    follow_up_after: date | None,
    applied_before: date | None,
    applied_after: date | None,
):
    if status_filter is not None:
        query = query.where(JobApplication.status == status_filter)

    if company is not None:
        query = query.where(JobApplication.company.ilike(f"%{company}%"))

    if role is not None:
        query = query.where(JobApplication.role_title.ilike(f"%{role}%"))

    if follow_up_before is not None:
        query = query.where(JobApplication.follow_up_date <= follow_up_before)

    if follow_up_after is not None:
        query = query.where(JobApplication.follow_up_date >= follow_up_after)

    if applied_before is not None:
        query = query.where(JobApplication.applied_date <= applied_before)

    if applied_after is not None:
        query = query.where(JobApplication.applied_date >= applied_after)

    return query


def application_csv_row(application: JobApplication) -> dict[str, str | int | None]:
    return {
        "id": application.id,
        "company": application.company,
        "role_title": application.role_title,
        "location": application.location,
        "status": str(application.status),
        "applied_date": application.applied_date,
        "follow_up_date": application.follow_up_date,
        "contact_name": application.contact_name,
        "contact_email": application.contact_email,
        "notes": application.notes,
        "created_at": application.created_at,
        "updated_at": application.updated_at,
    }


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
    needs_follow_up_by: date | None = None,
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

    if needs_follow_up_by is not None:
        query = query.where(
            JobApplication.follow_up_date.is_not(None),
            JobApplication.follow_up_date <= needs_follow_up_by,
        )

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


@router.get("/export.csv")
def export_applications_csv(
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    company: str | None = None,
    role: str | None = None,
    follow_up_before: date | None = None,
    follow_up_after: date | None = None,
    applied_before: date | None = None,
    applied_after: date | None = None,
    db: Session = Depends(get_db),
) -> Response:
    query = apply_application_export_filters(
        select(JobApplication),
        status_filter=status_filter,
        company=company,
        role=role,
        follow_up_before=follow_up_before,
        follow_up_after=follow_up_after,
        applied_before=applied_before,
        applied_after=applied_after,
    ).order_by(JobApplication.id.asc())
    applications = db.execute(query).scalars().all()

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_EXPORT_COLUMNS)
    writer.writeheader()
    for application in applications:
        writer.writerow(application_csv_row(application))

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="job_applications.csv"'},
    )


@router.post("", response_model=JobApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(
    application: JobApplicationCreate,
    db: Session = Depends(get_db),
) -> JobApplication:
    application_data = application.model_dump()
    if application_data["job_url"] is not None:
        application_data["job_url"] = str(application_data["job_url"])

    company = get_or_create_company(db, application_data["company"])
    application_data["company_id"] = company.id
    if application_data["contact_name"] is not None:
        contact = get_or_create_contact(
            db,
            company.id,
            application_data["contact_name"],
            application_data["contact_email"],
        )
        application_data["contact_id"] = contact.id

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


@router.get("/{application_id}/status-history", response_model=list[StatusHistoryRead])
def get_application_status_history(
    application_id: int,
    db: Session = Depends(get_db),
) -> list[ApplicationStatusHistory]:
    application = db.get(JobApplication, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    query = (
        select(ApplicationStatusHistory)
        .where(ApplicationStatusHistory.application_id == application_id)
        .order_by(
            ApplicationStatusHistory.changed_at.desc(),
            ApplicationStatusHistory.id.desc(),
        )
    )
    return db.execute(query).scalars().all()


@router.post(
    "/{application_id}/follow-up-reminders",
    response_model=FollowUpReminderRead,
    status_code=status.HTTP_201_CREATED,
)
def create_follow_up_reminder(
    application_id: int,
    reminder: FollowUpReminderCreate,
    db: Session = Depends(get_db),
) -> FollowUpReminder:
    application = db.get(JobApplication, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    db_reminder = FollowUpReminder(
        application_id=application_id,
        **reminder.model_dump(),
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


@router.get(
    "/{application_id}/follow-up-reminders",
    response_model=list[FollowUpReminderRead],
)
def list_follow_up_reminders(
    application_id: int,
    db: Session = Depends(get_db),
) -> list[FollowUpReminder]:
    application = db.get(JobApplication, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    query = (
        select(FollowUpReminder)
        .where(FollowUpReminder.application_id == application_id)
        .order_by(FollowUpReminder.reminder_date.asc(), FollowUpReminder.id.asc())
    )
    return db.execute(query).scalars().all()


@router.patch(
    "/{application_id}/follow-up-reminders/{reminder_id}",
    response_model=FollowUpReminderRead,
)
def update_follow_up_reminder(
    application_id: int,
    reminder_id: int,
    reminder_update: FollowUpReminderUpdate,
    db: Session = Depends(get_db),
) -> FollowUpReminder:
    application = db.get(JobApplication, application_id)
    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    reminder = db.get(FollowUpReminder, reminder_id)
    if reminder is None or reminder.application_id != application_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up reminder not found",
        )

    reminder.completed = reminder_update.completed
    db.commit()
    db.refresh(reminder)
    return reminder


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

    if "company" in update_data:
        company = get_or_create_company(db, update_data["company"])
        update_data["company_id"] = company.id
    else:
        company = application.company_record

    if update_data.get("contact_name") is not None:
        contact = get_or_create_contact(
            db,
            company.id,
            update_data["contact_name"],
            update_data.get("contact_email"),
        )
        update_data["contact_id"] = contact.id
    elif "contact_name" in update_data:
        update_data["contact_id"] = None

    old_status = application.status
    new_status = update_data.get("status")

    for field, value in update_data.items():
        setattr(application, field, value)

    if new_status is not None and new_status != old_status:
        db.add(
            ApplicationStatusHistory(
                application_id=application.id,
                old_status=str(old_status),
                new_status=str(new_status),
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
