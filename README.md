# Job Tracker API

A FastAPI backend for tracking job applications, interview stages, notes, and follow-up dates.

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- pytest
- Docker
- GitHub Actions

## Features

- Create, read, update, and delete job applications
- Track company, role, location, application status, notes, and follow-up date
- Filter applications by status, company, and follow-up date
- Store status changes over time
- Add notes to each application
- Validate incoming API requests with Pydantic
- Run automated tests with pytest
- Run locally with Docker Compose

## Local Development

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run the API:

```powershell
uvicorn app.main:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Run tests:

```powershell
pytest -v
```

## Docker

Run the API and PostgreSQL:

```powershell
docker compose up --build
```

Health check:

```text
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```
