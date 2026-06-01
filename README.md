# Job Tracker API

[![Tests](https://github.com/Dexter2099/Job-Tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/Dexter2099/Job-Tracker/actions/workflows/tests.yml)

A FastAPI backend for tracking job applications, interview stages, notes, and follow-up dates.

## Overview

Job Tracker API lets a user manage job applications through REST endpoints. The API validates request and response data with Pydantic, persists application data in PostgreSQL through SQLAlchemy models, and manages schema changes with Alembic migrations.

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
- Store status changes over time in a status history table
- Add notes to each application
- Validate incoming API requests with Pydantic
- Run automated tests with pytest
- Run locally with Docker Compose

## Architecture

```text
Client
  -> FastAPI route
  -> Pydantic schema validation
  -> SQLAlchemy model/session
  -> PostgreSQL
```

Alembic tracks database migrations, and GitHub Actions runs the pytest suite on pushes and pull requests.

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

Run database migrations:

```powershell
alembic upgrade head
```

## Docker

Run the API and PostgreSQL:

```powershell
docker compose up --build
```

Apply migrations after the database is running:

```powershell
alembic upgrade head
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

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Check API health |
| `POST` | `/applications` | Create a job application |
| `GET` | `/applications` | List job applications |
| `GET` | `/applications/{id}` | Get one job application |
| `PATCH` | `/applications/{id}` | Partially update a job application |
| `DELETE` | `/applications/{id}` | Delete a job application |

### List Applications

```text
GET /applications
```

Supported filters:

```text
GET /applications?status=interview
GET /applications?company=Atlassian
GET /applications?follow_up_before=2026-06-15
```

### Get Application

```text
GET /applications/{id}
```

### Create Application

```text
POST /applications
```

Example request:

```json
{
  "company": "Atlassian",
  "role_title": "Junior Backend Developer",
  "location": "Sydney",
  "job_url": "https://example.com/jobs/backend",
  "status": "applied",
  "source": "LinkedIn",
  "salary_range": "$80,000-$95,000",
  "notes": "Applied after tailoring resume.",
  "follow_up_date": "2026-06-15",
  "applied_date": "2026-05-31"
}
```

### Update Application

```text
PATCH /applications/{id}
```

Example request:

```json
{
  "status": "interview",
  "notes": "Phone screen booked.",
  "follow_up_date": "2026-06-20"
}
```

### Delete Application

```text
DELETE /applications/{id}
```
