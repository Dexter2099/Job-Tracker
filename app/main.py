from fastapi import Depends, FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import get_db
from app.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.middleware import RequestIDLoggingMiddleware
from app.routers import applications, stats


app = FastAPI(title="Job Tracker API")
app.add_middleware(RequestIDLoggingMiddleware)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.include_router(applications.router)
app.include_router(stats.router)


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
