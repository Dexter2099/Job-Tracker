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
- `companies` table
- `contacts` table
- `job_applications` table
- `job_applications.company_id` foreign key
- `job_applications.contact_id` optional foreign key
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
- First-class company model added:
  - applications create or reuse linked `companies` rows
  - application company updates relink `job_applications.company_id`
  - existing public application API contract still accepts and returns `company`
  - local SQLite tests and PostgreSQL-backed migration/test path verified
- First-class contact model added:
  - contacts belong to companies
  - applications can link to an optional contact
  - existing application endpoints accept and return optional `contact_name` and `contact_email`
  - contact creation and relinking covered by tests

## Current Slice

Contact table normalization:

- Added contact persistence without adding contact CRUD endpoints yet
- Linked contacts to companies and applications
- Preserved existing application create/list/get/update/delete behavior
- Kept the application API as the main workflow surface

## Next

- Add follow-up reminder records
- Link reminders to applications
- Keep the existing `follow_up_date` field working during the migration
- Add tests before schema/API changes

## Later Production Slices

- Frontend
- Authentication
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
