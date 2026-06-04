from collections.abc import Generator

from app.database import get_db
from app.main import app


def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_ok_when_database_is_reachable(client):
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}


def test_ready_response_includes_request_id(client):
    response = client.get("/ready")

    assert "X-Request-ID" in response.headers


def test_ready_returns_safe_503_when_database_check_fails(client):
    class FailingSession:
        def execute(self, statement):
            raise RuntimeError("database password leaked here")

    def override_get_db() -> Generator[FailingSession, None, None]:
        yield FailingSession()

    app.dependency_overrides[get_db] = override_get_db

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not_ready", "database": "error"}
