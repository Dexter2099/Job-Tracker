from datetime import date

from app.models import ApplicationStatusHistory, Company, Contact, JobApplication


def create_application(client, **overrides):
    payload = {
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
    }
    payload.update(overrides)
    response = client.post("/applications", json=payload)
    assert response.status_code == 201
    return response.json()


def assert_error_response(response, status_code, code, message):
    assert response.status_code == status_code
    assert response.json() == {
        "error": {
            "code": code,
            "message": message,
            "details": None,
            "request_id": response.headers["X-Request-ID"],
        }
    }


def test_create_application(client):
    data = create_application(client)
    assert data["id"] == 1
    assert data["company"] == "Atlassian"
    assert data["role_title"] == "Junior Backend Developer"
    assert data["status"] == "applied"
    assert data["follow_up_date"] == str(date(2026, 6, 15))
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_create_application_links_to_company_record(client, db_session):
    data = create_application(client, company="Atlassian")

    company = db_session.query(Company).one()
    application = db_session.get(JobApplication, data["id"])

    assert company.name == "Atlassian"
    assert application.company_id == company.id


def test_create_application_links_to_contact_record(client, db_session):
    data = create_application(
        client,
        company="Atlassian",
        contact_name="Priya Shah",
        contact_email="priya@example.com",
    )

    company = db_session.query(Company).filter_by(name="Atlassian").one()
    contact = db_session.query(Contact).one()
    application = db_session.get(JobApplication, data["id"])

    assert data["contact_name"] == "Priya Shah"
    assert data["contact_email"] == "priya@example.com"
    assert contact.name == "Priya Shah"
    assert contact.email == "priya@example.com"
    assert contact.company_id == company.id
    assert application.contact_id == contact.id


def test_list_applications(client):
    create_application(client, company="Atlassian", status="applied")
    create_application(client, company="Canva", status="interview")

    response = client.get("/applications")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert [application["company"] for application in data] == ["Canva", "Atlassian"]


def test_list_applications_uses_default_pagination_limit(client):
    for index in range(25):
        create_application(client, company=f"Company {index:02d}")

    response = client.get("/applications")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20
    assert data[0]["company"] == "Company 24"
    assert data[-1]["company"] == "Company 05"


def test_list_applications_supports_limit_and_offset(client):
    for index in range(5):
        create_application(client, company=f"Company {index:02d}")

    response = client.get("/applications?limit=2&offset=2")

    assert response.status_code == 200
    data = response.json()
    assert [application["company"] for application in data] == [
        "Company 02",
        "Company 01",
    ]


def test_list_applications_rejects_invalid_pagination_values(client):
    response = client.get("/applications?limit=0&offset=-1")

    assert response.status_code == 422


def test_get_application_by_id(client):
    created = create_application(client, company="Atlassian")

    response = client.get(f"/applications/{created['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["company"] == "Atlassian"


def test_get_missing_application_returns_404(client):
    response = client.get("/applications/999")

    assert_error_response(response, 404, "not_found", "Application not found")


def test_filter_applications_by_status(client):
    create_application(client, company="Atlassian", status="applied")
    create_application(client, company="Canva", status="interview")

    response = client.get("/applications?status=interview")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "Canva"
    assert data[0]["status"] == "interview"


def test_filter_applications_by_company(client):
    create_application(client, company="Atlassian")
    create_application(client, company="Canva")

    response = client.get("/applications?company=CAN")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "Canva"


def test_filter_applications_by_role(client):
    create_application(client, company="Atlassian", role_title="Junior Backend Developer")
    create_application(client, company="Canva", role_title="Product Designer")

    response = client.get("/applications?role=BACKEND")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "Atlassian"
    assert data[0]["role_title"] == "Junior Backend Developer"


def test_filter_applications_by_applied_date_range(client):
    create_application(client, company="Atlassian", applied_date="2026-05-31")
    create_application(client, company="Canva", applied_date="2026-06-05")
    create_application(client, company="Google", applied_date="2026-06-12")

    response = client.get(
        "/applications?applied_date_from=2026-06-01&applied_date_to=2026-06-10"
    )

    assert response.status_code == 200
    data = response.json()
    assert {application["company"] for application in data} == {"Canva"}


def test_filter_applications_by_follow_up_date_range(client):
    create_application(client, company="Atlassian", follow_up_date="2026-06-10")
    create_application(client, company="Canva", follow_up_date="2026-06-15")
    create_application(client, company="Google", follow_up_date="2026-06-20")

    response = client.get(
        "/applications?follow_up_date_from=2026-06-11&follow_up_date_to=2026-06-20"
    )

    assert response.status_code == 200
    data = response.json()
    assert {application["company"] for application in data} == {"Canva", "Google"}


def test_sort_applications_by_applied_date_desc(client):
    create_application(client, company="Atlassian", applied_date="2026-06-01")
    create_application(client, company="Canva", applied_date="2026-06-10")
    create_application(client, company="Google", applied_date="2026-06-05")

    response = client.get("/applications?sort=applied_date_desc")

    assert response.status_code == 200
    data = response.json()
    assert [application["company"] for application in data] == [
        "Canva",
        "Google",
        "Atlassian",
    ]


def test_filter_applications_combines_status_and_role(client):
    create_application(
        client,
        company="Atlassian",
        status="applied",
        role_title="Junior Backend Developer",
    )
    create_application(
        client,
        company="Canva",
        status="interview",
        role_title="Senior Backend Developer",
    )
    create_application(
        client,
        company="Google",
        status="applied",
        role_title="Product Designer",
    )

    response = client.get("/applications?status=applied&role=backend")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "Atlassian"


def test_filter_applications_by_follow_up_before(client):
    create_application(client, company="Atlassian", follow_up_date="2026-06-10")
    create_application(client, company="Canva", follow_up_date="2026-06-15")
    create_application(client, company="Google", follow_up_date="2026-06-20")

    response = client.get("/applications?follow_up_before=2026-06-15")

    assert response.status_code == 200
    data = response.json()
    assert {application["company"] for application in data} == {"Atlassian", "Canva"}


def test_filter_applications_by_follow_up_before_excludes_empty_dates(client):
    create_application(client, company="Atlassian", follow_up_date="2026-06-10")
    create_application(client, company="Canva", follow_up_date=None)

    response = client.get("/applications?follow_up_before=2026-06-15")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "Atlassian"


def test_filter_applications_needing_follow_up_by_date(client):
    create_application(client, company="Atlassian", follow_up_date="2026-06-10")
    create_application(client, company="Canva", follow_up_date="2026-06-15")
    create_application(client, company="Google", follow_up_date="2026-06-20")
    create_application(client, company="Microsoft", follow_up_date=None)

    response = client.get("/applications?needs_follow_up_by=2026-06-15")

    assert response.status_code == 200
    data = response.json()
    assert {application["company"] for application in data} == {"Atlassian", "Canva"}


def test_filter_applications_needing_follow_up_combines_with_status(client):
    create_application(
        client,
        company="Atlassian",
        status="applied",
        follow_up_date="2026-06-10",
    )
    create_application(
        client,
        company="Canva",
        status="interview",
        follow_up_date="2026-06-10",
    )
    create_application(
        client,
        company="Google",
        status="applied",
        follow_up_date="2026-06-20",
    )

    response = client.get("/applications?status=applied&needs_follow_up_by=2026-06-15")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "Atlassian"


def test_update_application(client):
    created = create_application(client, status="applied", notes="Initial note.")

    response = client.patch(
        f"/applications/{created['id']}",
        json={
            "status": "interview",
            "notes": "Phone screen booked.",
            "follow_up_date": "2026-06-20",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["status"] == "interview"
    assert data["notes"] == "Phone screen booked."
    assert data["follow_up_date"] == "2026-06-20"
    assert data["company"] == "Atlassian"


def test_update_application_relinks_company_record(client, db_session):
    created = create_application(client, company="Atlassian")

    response = client.patch(
        f"/applications/{created['id']}",
        json={"company": "Canva"},
    )

    application = db_session.get(JobApplication, created["id"])
    company = db_session.query(Company).filter_by(name="Canva").one()

    assert response.status_code == 200
    assert response.json()["company"] == "Canva"
    assert application.company_id == company.id


def test_update_application_relinks_contact_record(client, db_session):
    created = create_application(
        client,
        company="Atlassian",
        contact_name="Priya Shah",
        contact_email="priya@example.com",
    )

    response = client.patch(
        f"/applications/{created['id']}",
        json={
            "company": "Canva",
            "contact_name": "Jordan Lee",
            "contact_email": "jordan@example.com",
        },
    )

    company = db_session.query(Company).filter_by(name="Canva").one()
    contact = db_session.query(Contact).filter_by(email="jordan@example.com").one()
    application = db_session.get(JobApplication, created["id"])

    assert response.status_code == 200
    assert response.json()["contact_name"] == "Jordan Lee"
    assert response.json()["contact_email"] == "jordan@example.com"
    assert contact.company_id == company.id
    assert application.contact_id == contact.id


def test_update_missing_application_returns_404(client):
    response = client.patch("/applications/999", json={"status": "interview"})

    assert_error_response(response, 404, "not_found", "Application not found")


def test_update_application_rejects_invalid_status(client):
    created = create_application(client)

    response = client.patch(
        f"/applications/{created['id']}",
        json={"status": "not_a_real_status"},
    )

    assert response.status_code == 422


def test_status_history_model_uses_application_status_history_table():
    assert ApplicationStatusHistory.__tablename__ == "application_status_history"
    assert ApplicationStatusHistory.__table__.c.old_status.nullable is True
    assert str(ApplicationStatusHistory.__table__.c.old_status.type) == "VARCHAR(50)"
    assert str(ApplicationStatusHistory.__table__.c.new_status.type) == "VARCHAR(50)"


def test_update_application_status_creates_history_record(client, db_session):
    created = create_application(client, status="applied", notes="Initial note.")

    response = client.patch(
        f"/applications/{created['id']}",
        json={"status": "interview", "notes": "Phone screen booked."},
    )

    history_records = db_session.query(ApplicationStatusHistory).all()
    assert response.status_code == 200
    assert len(history_records) == 1
    assert history_records[0].application_id == created["id"]
    assert history_records[0].old_status == "applied"
    assert history_records[0].new_status == "interview"
    assert history_records[0].note == "Phone screen booked."
    assert history_records[0].changed_at is not None


def test_read_status_history_for_application(client):
    created = create_application(client, status="applied", notes="Initial note.")

    first_update_response = client.patch(
        f"/applications/{created['id']}",
        json={"status": "interview", "notes": "Phone screen booked."},
    )
    second_update_response = client.patch(
        f"/applications/{created['id']}",
        json={"status": "offer", "notes": "Offer received."},
    )
    response = client.get(f"/applications/{created['id']}/status-history")

    assert first_update_response.status_code == 200
    assert second_update_response.status_code == 200
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 2
    assert data[0]["application_id"] == created["id"]
    assert data[0]["old_status"] == "interview"
    assert data[0]["new_status"] == "offer"
    assert data[0]["changed_at"] is not None
    assert data[0]["note"] == "Offer received."
    assert data[1]["id"] == 1
    assert data[1]["old_status"] == "applied"
    assert data[1]["new_status"] == "interview"


def test_read_status_history_returns_empty_list_without_status_changes(client):
    created = create_application(client, status="applied")

    response = client.get(f"/applications/{created['id']}/status-history")

    assert response.status_code == 200
    assert response.json() == []


def test_read_status_history_for_missing_application_returns_404(client):
    response = client.get("/applications/999/status-history")

    assert_error_response(response, 404, "not_found", "Application not found")


def test_create_follow_up_reminder_for_application(client):
    created = create_application(client)

    response = client.post(
        f"/applications/{created['id']}/follow-up-reminders",
        json={"reminder_date": "2026-06-18", "note": "Send polite follow-up."},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["application_id"] == created["id"]
    assert data["reminder_date"] == "2026-06-18"
    assert data["note"] == "Send polite follow-up."
    assert data["completed"] is False
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_list_follow_up_reminders_returns_only_application_reminders(client):
    first = create_application(client, company="Atlassian")
    second = create_application(client, company="Canva")
    client.post(
        f"/applications/{first['id']}/follow-up-reminders",
        json={"reminder_date": "2026-06-18", "note": "Follow up with Atlassian."},
    )
    client.post(
        f"/applications/{second['id']}/follow-up-reminders",
        json={"reminder_date": "2026-06-19", "note": "Follow up with Canva."},
    )

    response = client.get(f"/applications/{first['id']}/follow-up-reminders")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["application_id"] == first["id"]
    assert data[0]["note"] == "Follow up with Atlassian."


def test_create_follow_up_reminder_for_missing_application_returns_404(client):
    response = client.post(
        "/applications/999/follow-up-reminders",
        json={"reminder_date": "2026-06-18", "note": "Send polite follow-up."},
    )

    assert_error_response(response, 404, "not_found", "Application not found")


def test_mark_follow_up_reminder_completed(client):
    created = create_application(client)
    reminder_response = client.post(
        f"/applications/{created['id']}/follow-up-reminders",
        json={"reminder_date": "2026-06-18", "note": "Send polite follow-up."},
    )

    response = client.patch(
        f"/applications/{created['id']}/follow-up-reminders/"
        f"{reminder_response.json()['id']}",
        json={"completed": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == reminder_response.json()["id"]
    assert data["application_id"] == created["id"]
    assert data["completed"] is True


def test_update_application_without_status_change_does_not_create_history(client, db_session):
    created = create_application(client, status="applied", notes="Initial note.")

    response = client.patch(
        f"/applications/{created['id']}",
        json={"notes": "Updated note only."},
    )

    history_records = db_session.query(ApplicationStatusHistory).all()
    assert response.status_code == 200
    assert history_records == []


def test_update_application_with_same_status_does_not_create_history(client, db_session):
    created = create_application(client, status="applied")

    response = client.patch(
        f"/applications/{created['id']}",
        json={"status": "applied", "notes": "Status remains applied."},
    )

    history_records = db_session.query(ApplicationStatusHistory).all()
    assert response.status_code == 200
    assert history_records == []


def test_delete_application_removes_status_history(client, db_session):
    created = create_application(client, status="applied")
    update_response = client.patch(
        f"/applications/{created['id']}",
        json={"status": "interview"},
    )

    delete_response = client.delete(f"/applications/{created['id']}")

    history_records = db_session.query(ApplicationStatusHistory).all()
    assert update_response.status_code == 200
    assert delete_response.status_code == 204
    assert history_records == []


def test_delete_application(client):
    created = create_application(client)

    delete_response = client.delete(f"/applications/{created['id']}")
    get_response = client.get(f"/applications/{created['id']}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert get_response.status_code == 404


def test_delete_missing_application_returns_404(client):
    response = client.delete("/applications/999")

    assert_error_response(response, 404, "not_found", "Application not found")
