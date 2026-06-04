from datetime import UTC, date, datetime, time, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ApplicationStatusHistory, FollowUpReminder, JobApplication
from app.schemas import WeeklyStatsRead


router = APIRouter(prefix="/stats", tags=["stats"])


def current_week_range() -> tuple[date, date]:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    return week_start, week_start + timedelta(days=6)


def as_utc_start(day: date) -> datetime:
    return datetime.combine(day, time.min, UTC)


def as_utc_exclusive_end(day: date) -> datetime:
    return datetime.combine(day + timedelta(days=1), time.min, UTC)


def count_scalar(db: Session, query) -> int:
    return db.execute(query).scalar_one()


@router.get("/weekly", response_model=WeeklyStatsRead)
def get_weekly_stats(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
) -> WeeklyStatsRead:
    default_start, default_end = current_week_range()
    week_start = start_date or default_start
    week_end = end_date or default_end
    changed_from = as_utc_start(week_start)
    changed_before = as_utc_exclusive_end(week_end)
    today = date.today()

    applications_sent = count_scalar(
        db,
        select(func.count()).select_from(JobApplication).where(
            JobApplication.applied_date >= week_start,
            JobApplication.applied_date <= week_end,
        ),
    )

    status_count_base = (
        select(func.count())
        .select_from(ApplicationStatusHistory)
        .where(
            ApplicationStatusHistory.changed_at >= changed_from,
            ApplicationStatusHistory.changed_at < changed_before,
        )
    )
    interviews = count_scalar(
        db,
        status_count_base.where(
            ApplicationStatusHistory.new_status.in_(
                ["interview", "technical_interview"]
            )
        ),
    )
    rejections = count_scalar(
        db,
        status_count_base.where(ApplicationStatusHistory.new_status == "rejected"),
    )
    offers = count_scalar(
        db,
        status_count_base.where(ApplicationStatusHistory.new_status == "offer"),
    )

    follow_ups_due = count_scalar(
        db,
        select(func.count()).select_from(FollowUpReminder).where(
            FollowUpReminder.completed.is_(False),
            FollowUpReminder.reminder_date >= week_start,
            FollowUpReminder.reminder_date <= week_end,
        ),
    )
    overdue_follow_ups = count_scalar(
        db,
        select(func.count()).select_from(FollowUpReminder).where(
            FollowUpReminder.completed.is_(False),
            FollowUpReminder.reminder_date < today,
        ),
    )

    return WeeklyStatsRead(
        week_start=week_start,
        week_end=week_end,
        applications_sent=applications_sent,
        interviews=interviews,
        rejections=rejections,
        offers=offers,
        follow_ups_due=follow_ups_due,
        overdue_follow_ups=overdue_follow_ups,
    )
