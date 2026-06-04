# Project Progress

This file tracks the Job Tracker API production-readiness path so the project
stays focused.

## Current Baseline

- FastAPI backend
- PostgreSQL persistence
- SQLAlchemy models
- Alembic migrations
- pytest coverage
- Docker Compose local development
- GitHub Actions test workflow
- README documentation

## Completed

- Project scaffold
- `GET /health`
- Docker Compose PostgreSQL setup
- SQLAlchemy database connection
- Alembic migration setup
- `job_applications` table
- `POST /applications`
- `GET /applications`
- `GET /applications/{application_id}`
- `PATCH /applications/{application_id}`
- `DELETE /applications/{application_id}`
- Filter applications by `status`
- Filter applications by `company`
- Filter applications by `follow_up_before`
- Filter applications needing follow-up by date
- `application_status_history` table
- Automatic status history record when application status changes
- API endpoint to read status history
- Alembic status-history migration verified against Docker PostgreSQL
- Focused status-history edge-case tests
- README API examples polished
- GitHub Actions workflow test command hardened
- Docker Compose end-to-end app run verified
- README clone-to-running setup documented
- README example responses documented
- Interview explanation documented
- Swagger/API screenshot added for portfolio polish
- Production-readiness roadmap defined
- Baseline verified on 2026-06-04:
  - `python -m pytest -v` passed locally
  - `docker compose up --build -d` started API and PostgreSQL
  - Alembic migrations applied against a temporary clean PostgreSQL database
  - running Docker API returned `{"status": "ok"}` from `/health`

## Current Slice

Production readiness baseline:

- Confirmed current API/test/Docker/migration baseline is healthy
- Confirmed this slice started from a clean branch against `origin/main`
- Next code slice should improve the domain model without widening scope

## Next

- Add a first-class `companies` table
- Link job applications to companies with a foreign key
- Preserve existing application API behavior during the migration
- Add tests before schema/API changes

## Later Production Slices

- Frontend
- Authentication
- Contacts/recruiters
- Weekly stats
- CSV export
- Structured logging and request IDs
- Production deployment
- Role-based access
- AI matching
- Email integration
- Web scraping
- Resume parsing
- Job board sync
- Analytics dashboard
