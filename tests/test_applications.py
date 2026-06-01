from datetime import date


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


def test_create_application(client):
    data = create_application(client)
    assert data["id"] == 1
    assert data["company"] == "Atlassian"
    assert data["role_title"] == "Junior Backend Developer"
    assert data["status"] == "applied"
    assert data["follow_up_date"] == str(date(2026, 6, 15))
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_list_applications(client):
    create_application(client, company="Atlassian", status="applied")
    create_application(client, company="Canva", status="interview")

    response = client.get("/applications")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert [application["company"] for application in data] == ["Atlassian", "Canva"]


def test_get_application_by_id(client):
    created = create_application(client, company="Atlassian")

    response = client.get(f"/applications/{created['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["company"] == "Atlassian"


def test_get_missing_application_returns_404(client):
    response = client.get("/applications/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Application not found"}


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

    response = client.get("/applications?company=can")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["company"] == "Canva"
