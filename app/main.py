from typing import Annotated
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, Form, Query, Request
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import get_db
from app.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.middleware import RequestIDLoggingMiddleware
from app.models import ApplicationStatus, JobApplication
from app.routers import applications, stats
from app.schemas import JobApplicationCreate, JobApplicationUpdate


app = FastAPI(title="Job Tracker API")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(RequestIDLoggingMiddleware)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.include_router(applications.router)
app.include_router(stats.router)
templates = Jinja2Templates(directory="app/templates")


def empty_to_none(value: str | None) -> str | None:
    if value is None or value.strip() == "":
        return None
    return value.strip()


def dashboard_redirect(status_filter: ApplicationStatus | None = None) -> RedirectResponse:
    url = "/"
    if status_filter is not None:
        url = f"/?{urlencode({'status': status_filter.value})}"
    return RedirectResponse(url=url, status_code=303)


@app.get("/")
def dashboard(
    request: Request,
    status_filter: Annotated[ApplicationStatus | None, Query(alias="status")] = None,
    db: Session = Depends(get_db),
):
    query = select(JobApplication)
    if status_filter is not None:
        query = query.where(JobApplication.status == status_filter)
    query = query.order_by(JobApplication.created_at.desc(), JobApplication.id.desc())
    application_rows = db.execute(query.limit(100)).scalars().all()

    ready_status = "ready"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        ready_status = "not_ready"

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "applications": application_rows,
            "statuses": list(ApplicationStatus),
            "selected_status": status_filter,
            "health_status": "ok",
            "ready_status": ready_status,
        },
    )


@app.post("/dashboard/applications")
def dashboard_create_application(
    company: Annotated[str, Form()],
    role_title: Annotated[str, Form()],
    location: Annotated[str | None, Form()] = None,
    status: Annotated[ApplicationStatus, Form()] = ApplicationStatus.applied,
    job_url: Annotated[str | None, Form()] = None,
    source: Annotated[str | None, Form()] = None,
    notes: Annotated[str | None, Form()] = None,
    db: Session = Depends(get_db),
):
    application = JobApplicationCreate(
        company=company,
        role_title=role_title,
        location=empty_to_none(location),
        status=status,
        job_url=empty_to_none(job_url),
        source=empty_to_none(source),
        notes=empty_to_none(notes),
    )
    applications.create_application(application, db)
    return dashboard_redirect()


@app.post("/dashboard/applications/{application_id}/status")
def dashboard_update_application_status(
    application_id: int,
    status: Annotated[ApplicationStatus, Form()],
    current_filter: Annotated[ApplicationStatus | None, Form()] = None,
    db: Session = Depends(get_db),
):
    applications.update_application(
        application_id,
        JobApplicationUpdate(status=status),
        db,
    )
    return dashboard_redirect(current_filter)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get(
    "/ready",
    tags=["operations"],
    summary="Check database readiness",
)
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "database": "error"},
        )
    return {"status": "ready", "database": "ok"}
