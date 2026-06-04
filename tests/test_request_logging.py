import json
from uuid import UUID


def request_logs(caplog):
    return [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "job_tracker.requests"
    ]


def test_response_includes_generated_request_id(client):
    response = client.get("/health")

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]
    assert UUID(request_id).version == 4


def test_response_reuses_incoming_request_id(client):
    response = client.get("/health", headers={"X-Request-ID": "test-request-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-123"


def test_404_response_includes_request_id(client):
    response = client.get("/missing")

    assert response.status_code == 404
    assert UUID(response.headers["X-Request-ID"]).version == 4


def test_request_log_includes_structured_fields(client, caplog):
    caplog.set_level("INFO", logger="job_tracker.requests")

    response = client.get("/health", headers={"X-Request-ID": "log-request-123"})

    logs = request_logs(caplog)
    assert response.status_code == 200
    assert len(logs) == 1
    assert logs[0]["request_id"] == "log-request-123"
    assert logs[0]["method"] == "GET"
    assert logs[0]["path"] == "/health"
    assert logs[0]["status_code"] == 200
    assert isinstance(logs[0]["duration_ms"], float)
    assert logs[0]["duration_ms"] >= 0
