from fastapi import FastAPI

from app.middleware import RequestIDLoggingMiddleware
from app.routers import applications, stats


app = FastAPI(title="Job Tracker API")
app.add_middleware(RequestIDLoggingMiddleware)
app.include_router(applications.router)
app.include_router(stats.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
