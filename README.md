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

Clone the repository:

```powershell
git clone https://github.com/Dexter2099/Job-Tracker.git
cd Job-Tracker
```

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

Open the API docs:

```text
http://127.0.0.1:8000/docs
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

## Screenshots

### Swagger UI

![Swagger UI overview](docs/screenshots/swagger-overview.png)

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Check API health |
| `POST` | `/applications` | Create a job application |
| `GET` | `/applications` | List job applications |
| `GET` | `/applications/{id}` | Get one job application |
| `GET` | `/applications/{id}/status-history` | List status history for one job application |
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
GET /applications?needs_follow_up_by=2026-06-15
```

`needs_follow_up_by` returns applications with a follow-up date due on or before
the supplied date.

Pagination:

```text
GET /applications?limit=20&offset=0
GET /applications?status=interview&limit=10&offset=20
```

`limit` defaults to `20` and accepts values from `1` to `100`. `offset`
defaults to `0`.

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

Example response:

```json
{
  "id": 1,
  "company": "Atlassian",
  "role_title": "Junior Backend Developer",
  "location": "Sydney",
  "job_url": "https://example.com/jobs/backend",
  "status": "applied",
  "source": "LinkedIn",
  "salary_range": "$80,000-$95,000",
  "notes": "Applied after tailoring resume.",
  "follow_up_date": "2026-06-15",
  "applied_date": "2026-05-31",
  "created_at": "2026-06-01T04:12:38.411147Z",
  "updated_at": "2026-06-01T04:12:38.411147Z"
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

Example response:

```json
{
  "id": 1,
  "company": "Atlassian",
  "role_title": "Junior Backend Developer",
  "location": "Sydney",
  "job_url": "https://example.com/jobs/backend",
  "status": "interview",
  "source": "LinkedIn",
  "salary_range": "$80,000-$95,000",
  "notes": "Phone screen booked.",
  "follow_up_date": "2026-06-20",
  "applied_date": "2026-05-31",
  "created_at": "2026-06-01T04:12:38.411147Z",
  "updated_at": "2026-06-01T04:12:38.446502Z"
}
```

### Delete Application

```text
DELETE /applications/{id}
```

Successful deletes return:

```text
204 No Content
```

## Interview Explanation

Job Tracker API is a FastAPI backend for managing job applications. A client sends HTTP requests to API endpoints, Pydantic validates and serializes request and response data, the route layer handles the API operation, SQLAlchemy maps Python models to PostgreSQL tables, and Alembic manages database schema changes over time. The project uses pytest for API behavior tests, Docker Compose for local PostgreSQL development, and GitHub Actions for continuous integration.
