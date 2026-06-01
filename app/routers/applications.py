from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ApplicationStatus, JobApplication
from app.schemas import JobApplicationCreate, JobApplicationRead, JobApplicationUpdate


router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[JobApplicationRead])
def list_applications(
    status_filter: ApplicationStatus | None = Query(default=None, alias="status"),
    company: str | None = None,
    follow_up_before: date | None = None,
    db: Session = Depends(get_db),
) -> list[JobApplication]:
    query = db.query(JobApplication)

    if status_filter is not None:
        query = query.filter(JobApplication.status == status_filter)

    if company is not None:
        query = query.filter(JobApplication.company.ilike(f"%{company}%"))

    if follow_up_before is not None:
        query = query.filter(JobApplication.follow_up_date <= follow_up_before)

    return query.order_by(JobApplication.id).all()


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

    for field, value in update_data.items():
        setattr(application, field, value)

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
