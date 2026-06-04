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

## Current Slice

Final README and Docker polish:

- Verified `docker compose up --build`
- Verified migrations against Docker PostgreSQL
- Verified health, create, and update through the running API
- Added clone-to-running setup steps
- Added example responses
- Added interview explanation

## Next

- Add Swagger/API screenshots for portfolio polish

## Later, Not MVP

- Frontend
- Authentication
- AI matching
- Email integration
- Web scraping
- Resume parsing
- Job board sync
- Analytics dashboard
