from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import JobApplication
from app.schemas import JobApplicationCreate, JobApplicationRead


router = APIRouter(prefix="/applications", tags=["applications"])


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
