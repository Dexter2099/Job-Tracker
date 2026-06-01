# Project Progress

This file tracks the Job Tracker API MVP so the project stays focused.

## MVP Scope

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
- `status_history` table
- Automatic status history record when application status changes
- Alembic status-history migration verified against Docker PostgreSQL
- Focused status-history edge-case tests
- README API examples polished
- GitHub Actions workflow test command hardened

## Current Slice

README and CI polish:

- Added CI status badge
- Clarified project architecture
- Added endpoint summary table
- Verified tests in a Linux Python container

## Next

- Confirm latest GitHub Actions run passes after this workflow update

## Later, Not MVP

- API endpoint to read status history
- Frontend
- Authentication
- AI matching
- Email integration
- Web scraping
- Resume parsing
- Job board sync
- Analytics dashboard
