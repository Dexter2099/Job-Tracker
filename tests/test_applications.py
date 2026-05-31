from datetime import date


def test_create_application(client):
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

    response = client.post("/applications", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["company"] == payload["company"]
    assert data["role_title"] == payload["role_title"]
    assert data["status"] == payload["status"]
    assert data["follow_up_date"] == str(date(2026, 6, 15))
    assert data["created_at"] is not None
    assert data["updated_at"] is not None
