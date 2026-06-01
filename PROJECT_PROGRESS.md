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

## Current Slice

Status history persistence:

- Record `application_id`
- Record `old_status`
- Record `new_status`
- Record `changed_at`
- Record update note when supplied

## Next

- Add focused tests for status history edge cases
- Polish README examples and GitHub Actions status

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
