from fastapi import FastAPI

from app.routers import applications


app = FastAPI(title="Job Tracker API")
app.include_router(applications.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
