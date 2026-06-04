import csv
from io import StringIO


EXPECTED_COLUMNS = [
    "id",
    "company",
    "role_title",
    "location",
    "status",
    "applied_date",
    "follow_up_date",
    "contact_name",
    "contact_email",
    "notes",
    "created_at",
    "updated_at",
]


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
        "contact_name": "Priya Shah",
        "contact_email": "priya@example.com",
    }
    payload.update(overrides)
    response = client.post("/applications", json=payload)
    assert response.status_code == 201
    return response.json()


def parse_csv(response):
    return list(csv.DictReader(StringIO(response.text)))


def test_export_applications_csv_returns_downloadable_csv(client):
    create_application(client, company="Atlassian")

    response = client.get("/applications/export.csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    assert "job_applications.csv" in response.headers["content-disposition"]


def test_export_applications_csv_header_contains_expected_columns(client):
    response = client.get("/applications/export.csv")

    header = response.text.splitlines()[0].split(",")
    assert header == EXPECTED_COLUMNS


def test_export_applications_csv_includes_created_applications_in_id_order(client):
    first = create_application(client, company="Atlassian")
    second = create_application(client, company="Canva", status="interview")

    response = client.get("/applications/export.csv")

    rows = parse_csv(response)
    assert [row["id"] for row in rows] == [str(first["id"]), str(second["id"])]
    assert rows[0]["company"] == "Atlassian"
    assert rows[0]["role_title"] == "Junior Backend Developer"
    assert rows[0]["location"] == "Sydney"
    assert rows[0]["status"] == "applied"
    assert rows[0]["applied_date"] == "2026-05-31"
    assert rows[0]["follow_up_date"] == "2026-06-15"
    assert rows[0]["contact_name"] == "Priya Shah"
    assert rows[0]["contact_email"] == "priya@example.com"
    assert rows[0]["notes"] == "Applied after tailoring resume."


def test_export_applications_csv_filters_by_status(client):
    create_application(client, company="Atlassian", status="applied")
    create_application(client, company="Canva", status="interview")

    response = client.get("/applications/export.csv?status=interview")

    rows = parse_csv(response)
    assert len(rows) == 1
    assert rows[0]["company"] == "Canva"
    assert rows[0]["status"] == "interview"


def test_export_applications_csv_filters_by_company(client):
    create_application(client, company="Atlassian")
    create_application(client, company="Canva")

    response = client.get("/applications/export.csv?company=CAN")

    rows = parse_csv(response)
    assert len(rows) == 1
    assert rows[0]["company"] == "Canva"


def test_export_applications_csv_empty_result_returns_headers(client):
    create_application(client, company="Atlassian")

    response = client.get("/applications/export.csv?company=Missing")

    assert response.status_code == 200
    assert response.text.splitlines() == [",".join(EXPECTED_COLUMNS)]
    assert parse_csv(response) == []
