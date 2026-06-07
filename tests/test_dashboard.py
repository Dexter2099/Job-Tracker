def test_dashboard_returns_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Job Tracker API" in response.text
    assert "/docs" in response.text
    assert "/health" in response.text
    assert "/ready" in response.text


def test_dashboard_lists_applications_and_filters_by_status(client):
    client.post(
        "/applications",
        json={
            "company": "Atlassian",
            "role_title": "Junior Backend Developer",
            "status": "applied",
        },
    )
    client.post(
        "/applications",
        json={
            "company": "Canva",
            "role_title": "Junior API Developer",
            "status": "interview",
        },
    )

    response = client.get("/?status=interview")

    assert response.status_code == 200
    assert "Canva" in response.text
    assert "Junior API Developer" in response.text
    assert "Atlassian" not in response.text


def test_dashboard_create_and_status_update_helpers_redirect(client):
    create_response = client.post(
        "/dashboard/applications",
        data={
            "company": "Atlassian",
            "role_title": "Junior Backend Developer",
            "location": "Brisbane",
            "status": "applied",
        },
        follow_redirects=False,
    )
    assert create_response.status_code == 303

    dashboard_response = client.get("/")
    assert "Atlassian" in dashboard_response.text
    assert "applied" in dashboard_response.text

    update_response = client.post(
        "/dashboard/applications/1/status",
        data={"status": "interview"},
        follow_redirects=False,
    )
    assert update_response.status_code == 303

    filtered_response = client.get("/?status=interview")
    assert "Atlassian" in filtered_response.text
    assert "interview" in filtered_response.text
