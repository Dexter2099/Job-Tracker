# Job Tracker API

[![Tests](https://github.com/Dexter2099/Job-Tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/Dexter2099/Job-Tracker/actions/workflows/tests.yml)

A production-hardened FastAPI backend for tracking job applications, companies,
recruiter contacts, status history, follow-up reminders, weekly job-search
stats, and CSV export.

## Overview

Job Tracker API lets a user manage a job search through REST endpoints. The API
validates request and response data with Pydantic, persists normalized
application data in PostgreSQL through SQLAlchemy models, and manages schema
changes with Alembic migrations. It also includes production-style backend
behaviour: request IDs, structured JSON request logs, standardized error
responses, health/readiness checks, Docker Compose local development, seed data,
and PostgreSQL-backed CI.

This project is intentionally kept as a $0 portfolio version. It is not deployed
to a public free tier because free databases can expire, cold starts make demos
unreliable, and the local Docker Compose workflow gives a more repeatable
interview walkthrough.

## What This Project Demonstrates

- REST API design
- FastAPI routing
- Pydantic request/response validation
- SQLAlchemy ORM modelling
- PostgreSQL persistence
- Alembic migrations
- Docker Compose local environment
- pytest coverage
- PostgreSQL-backed CI
- Production API behaviour: request IDs, JSON logging, standardized errors
- Operational health/readiness endpoints

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
- Store companies in a first-class table linked from job applications
- Store recruiter/contact records linked to companies and applications
- Store first-class follow-up reminder records linked to applications
- Return weekly job-search statistics
- Export job applications as CSV
- Add request IDs to responses and structured request logs
- Filter applications by status, company, and follow-up date
- Store status changes over time in a status history table
- Add notes to each application
- Validate incoming API requests with Pydantic
- Run automated tests with pytest
- Run locally with Docker Compose

## Architecture

```text
Client
  -> FastAPI routers
  -> Pydantic schemas
  -> SQLAlchemy session/models
  -> PostgreSQL
  -> Alembic migrations
  -> pytest + GitHub Actions verification
```

Alembic tracks database migrations, including the normalized `companies` and
`contacts` tables, follow-up reminder records, and application foreign keys.
GitHub Actions runs the pytest suite on pushes and pull requests.

## Schema Overview

| Table | Purpose |
| --- | --- |
| `companies` | Stores each company once so applications and contacts can link to a shared company record. |
| `contacts` | Stores recruiter or hiring contact details linked to a company. |
| `job_applications` | Stores the main job application record, including role, status, dates, notes, and optional company/contact links. |
| `application_status_history` | Stores status transitions so application progress can be audited over time. |
| `follow_up_reminders` | Stores durable follow-up reminders linked to applications. |

## Production-Hardening Features

- Request ID middleware adds `X-Request-ID` to every response
- Structured JSON request logging records request ID, method, path, status code, and duration
- Standardized error responses wrap HTTP, validation, and unhandled errors
- `/health` checks the API process; `/ready` checks database readiness
- Pagination keeps list responses bounded
- CSV export provides a deterministic download path for applications
- Weekly stats summarize application activity and follow-up work
- PostgreSQL-backed CI verifies migrations and tests against a real database
- Repeatable seed data creates a local demo dataset without uncontrolled duplicates

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

## Demo Frontend

The repo includes an intentionally thin server-rendered dashboard for portfolio
videos. It exists only to make the FastAPI/PostgreSQL backend visible during a
short demo; the API remains the main project surface.

Run it with:

```powershell
uvicorn app.main:app --reload
```

Open the dashboard:

```text
http://127.0.0.1:8000/
```

API docs:

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

Seed local demo data:

```powershell
python scripts/seed_data.py
```

The seed script creates a small fixed demo dataset for Swagger walkthroughs,
weekly stats, reminders, and CSV export. It is safe to run more than once:
known seed records are skipped instead of duplicated.

## Run The Demo Locally

```powershell
git clone https://github.com/Dexter2099/Job-Tracker.git
cd Job-Tracker
pip install -r requirements.txt
docker compose up --build
alembic upgrade head
python scripts/seed_data.py
```

Then open:

```text
http://127.0.0.1:8000/docs
```

Run the test suite:

```powershell
python -m pytest -v
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

## Operational Endpoints

`GET /health` checks that the API process is alive.

`GET /ready` checks that the API can connect to the database with a simple
readiness query.

Ready response:

```json
{
  "status": "ready",
  "database": "ok"
}
```

Not ready response:

```json
{
  "status": "not_ready",
  "database": "error"
}
```

## Production Behavior

Every response includes an `X-Request-ID` header. If the client sends
`X-Request-ID`, the API reuses it; otherwise it generates a UUID4 value. Each
request also emits one JSON log line through the `job_tracker.requests` logger
with `request_id`, `method`, `path`, `status_code`, and `duration_ms`.

Handled errors use a consistent response shape:

```json
{
  "error": {
    "code": "not_found",
    "message": "Application not found",
    "details": null,
    "request_id": "..."
  }
}
```

## Why Not Deployed?

Deployment is intentionally skipped to keep the project at $0 and avoid an
unreliable portfolio link caused by free-tier cold starts, sleeping services, or
expiring databases. The project can still be run locally with Docker Compose,
and it demonstrates deployment readiness through Docker, Alembic migrations,
health/readiness endpoints, GitHub Actions, and environment-based database
configuration. No private job-tracker data is committed.

## Screenshots

### Swagger UI

![Swagger UI overview](docs/screenshots/swagger-overview.png)

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Check API health |
| `GET` | `/ready` | Check database readiness |
| `POST` | `/applications` | Create a job application |
| `GET` | `/applications` | List job applications |
| `GET` | `/applications/export.csv` | Export job applications as CSV |
| `GET` | `/applications/{id}` | Get one job application |
| `GET` | `/applications/{id}/status-history` | List status history for one job application |
| `POST` | `/applications/{id}/follow-up-reminders` | Create a follow-up reminder |
| `GET` | `/applications/{id}/follow-up-reminders` | List follow-up reminders |
| `PATCH` | `/applications/{id}/follow-up-reminders/{reminder_id}` | Mark a reminder completed |
| `PATCH` | `/applications/{id}` | Partially update a job application |
| `DELETE` | `/applications/{id}` | Delete a job application |
| `GET` | `/stats/weekly` | Return weekly application and follow-up statistics |

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

### Export Applications

```text
GET /applications/export.csv
GET /applications/export.csv?status=interview&company=Canva
```

The response is `text/csv` with a `Content-Disposition` attachment header and
these columns:

```text
id,company,role_title,location,status,applied_date,follow_up_date,contact_name,contact_email,notes,created_at,updated_at
```

### Get Application

```text
GET /applications/{id}
```

### Status History

When an application's `status` changes, the API stores a row in
`application_status_history` with the previous status, new status, change
timestamp, and the update note when one is provided.

```text
GET /applications/{id}/status-history
```

Status history is returned newest first.

### Follow-Up Reminders

Applications still support the simple `follow_up_date` field. For durable
follow-up tracking, reminders can also be stored as first-class records linked
to an application.

```text
POST /applications/{id}/follow-up-reminders
```

Example request:

```json
{
  "reminder_date": "2026-06-18",
  "note": "Send polite follow-up."
}
```

```text
GET /applications/{id}/follow-up-reminders
PATCH /applications/{id}/follow-up-reminders/{reminder_id}
```

Mark a reminder completed:

```json
{
  "completed": true
}
```

### Weekly Stats

```text
GET /stats/weekly
GET /stats/weekly?start_date=2026-06-01&end_date=2026-06-07
```

Example response:

```json
{
  "week_start": "2026-06-01",
  "week_end": "2026-06-07",
  "applications_sent": 4,
  "interviews": 1,
  "rejections": 1,
  "offers": 1,
  "follow_ups_due": 2,
  "overdue_follow_ups": 1
}
```

### Create Application

```text
POST /applications
```

The public API still accepts a `company` string for a job application. Internally,
the API creates or reuses a matching row in `companies` and links the application
with `job_applications.company_id`. Optional `contact_name` and `contact_email`
fields create or reuse a linked `contacts` row for that company.

Example request:

```json
{
  "company": "Atlassian",
  "role_title": "Junior Backend Developer",
  "location": "Sydney",
  "job_url": "https://example.com/jobs/backend",
  "status": "applied",
  "source": "LinkedIn",
  "contact_name": "Priya Shah",
  "contact_email": "priya@example.com",
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
  "contact_name": "Priya Shah",
  "contact_email": "priya@example.com",
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
  "contact_name": "Jordan Lee",
  "contact_email": "jordan@example.com",
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
  "contact_name": "Jordan Lee",
  "contact_email": "jordan@example.com",
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

## How I Would Explain This In An Interview

Job Tracker API is a FastAPI/PostgreSQL backend for managing job applications,
companies, recruiter contacts, status history, follow-up reminders, weekly
stats, and CSV export.

When a client sends a request, FastAPI routes it to the correct handler,
Pydantic validates the request and response shape, SQLAlchemy uses a database
session to read or write models, PostgreSQL stores the data, and Alembic keeps
schema changes versioned. The test suite verifies the API locally and in
PostgreSQL-backed CI.

I normalized companies and contacts because the same company or recruiter can
appear across multiple applications, and duplicating those fields inside every
application would make the data harder to maintain. Status history and
follow-up reminders make the domain model stronger: they preserve how an
application changed over time and turn follow-up work into durable records
instead of a single date field.

I hardened the API with request IDs, structured JSON logs, standardized error
responses, pagination, CSV export, seed data, and separate `/health` and
`/ready` endpoints. I intentionally left out auth and public deployment for this
portfolio version so the project stays focused, free to run, and easy to demo
locally. A deliberate production-realism path would add auth and user-owned
data next.
