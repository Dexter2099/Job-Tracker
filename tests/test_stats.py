from datetime import UTC, date, datetime, timedelta

from app.models import ApplicationStatusHistory


def current_week_range() -> tuple[date, date]:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def create_application(client, **overrides):
    payload = {
        "company": "Atlassian",
        "role_title": "Junior Backend Developer",
        "status": "applied",
        "applied_date": str(date.today()),
    }
    payload.update(overrides)
    response = client.post("/applications", json=payload)
    assert response.status_code == 201
    return response.json()


def create_reminder(client, application_id: int, reminder_date: date, completed=False):
    response = client.post(
        f"/applications/{application_id}/follow-up-reminders",
        json={"reminder_date": str(reminder_date), "note": "Follow up."},
    )
    assert response.status_code == 201
    if completed:
        complete_response = client.patch(
            f"/applications/{application_id}/follow-up-reminders/"
            f"{response.json()['id']}",
            json={"completed": True},
        )
        assert complete_response.status_code == 200
    return response.json()


def add_status_history(db_session, application_id: int, new_status: str, changed_on: date):
    db_session.add(
        ApplicationStatusHistory(
            application_id=application_id,
            old_status="applied",
            new_status=new_status,
            changed_at=datetime.combine(changed_on, datetime.min.time(), UTC),
        )
    )
    db_session.commit()


def test_default_weekly_stats(client, db_session):
    week_start, week_end = current_week_range()
    today = date.today()
    applied = create_application(client, company="Applied Co", applied_date=str(today))
    interview = create_application(client, company="Interview Co", applied_date=str(today))
    rejected = create_application(client, company="Rejected Co", applied_date=str(today))
    offer = create_application(client, company="Offer Co", applied_date=str(today))

    add_status_history(db_session, interview["id"], "interview", today)
    add_status_history(db_session, rejected["id"], "rejected", today)
    add_status_history(db_session, offer["id"], "offer", today)
    create_reminder(client, applied["id"], week_start)

    response = client.get("/stats/weekly")

    assert response.status_code == 200
    assert response.json() == {
        "week_start": str(week_start),
        "week_end": str(week_end),
        "applications_sent": 4,
        "interviews": 1,
        "rejections": 1,
        "offers": 1,
        "follow_ups_due": 1,
        "overdue_follow_ups": 1 if week_start < today else 0,
    }


def test_weekly_stats_accepts_custom_date_range(client, db_session):
    start_date = date(2026, 6, 1)
    end_date = date(2026, 6, 7)
    in_range = create_application(
        client,
        company="In Range",
        applied_date=str(start_date),
    )
    create_application(
        client,
        company="Out Range",
        applied_date="2026-06-08",
    )
    add_status_history(db_session, in_range["id"], "interview", start_date)
    create_reminder(client, in_range["id"], date(2026, 6, 3))

    response = client.get(
        "/stats/weekly?start_date=2026-06-01&end_date=2026-06-07"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["week_start"] == "2026-06-01"
    assert data["week_end"] == "2026-06-07"
    assert data["applications_sent"] == 1
    assert data["interviews"] == 1
    assert data["follow_ups_due"] == 1


def test_weekly_stats_excludes_completed_reminders_from_due_count(client):
    week_start, _ = current_week_range()
    application = create_application(client)
    create_reminder(client, application["id"], week_start, completed=True)

    response = client.get("/stats/weekly")

    assert response.status_code == 200
    assert response.json()["follow_ups_due"] == 0


def test_weekly_stats_counts_overdue_incomplete_reminders(client):
    application = create_application(client)
    create_reminder(client, application["id"], date.today() - timedelta(days=1))

    response = client.get("/stats/weekly")

    assert response.status_code == 200
    assert response.json()["overdue_follow_ups"] == 1


def test_weekly_stats_excludes_out_of_range_applications_and_reminders(client):
    create_application(client, applied_date="2026-05-31")
    in_range = create_application(client, applied_date="2026-06-02")
    create_reminder(client, in_range["id"], date(2026, 6, 8))

    response = client.get(
        "/stats/weekly?start_date=2026-06-01&end_date=2026-06-07"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["applications_sent"] == 1
    assert data["follow_ups_due"] == 0
