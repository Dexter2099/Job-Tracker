import asyncio
import json

from starlette.requests import Request

from app.errors import unhandled_exception_handler


def assert_standard_error(response, code, message, status_code):
    request_id = response.headers["X-Request-ID"]

    assert response.status_code == status_code
    assert response.json()["error"]["code"] == code
    assert response.json()["error"]["message"] == message
    assert response.json()["error"]["request_id"] == request_id
    assert "details" in response.json()["error"]


def test_missing_application_uses_standardized_error_shape(client):
    response = client.get(
        "/applications/999",
        headers={"X-Request-ID": "missing-application-request"},
    )

    assert_standard_error(
        response,
        code="not_found",
        message="Application not found",
        status_code=404,
    )
    assert response.json()["error"]["details"] is None


def test_unhandled_exception_handler_hides_internal_details():
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/boom",
            "headers": [(b"x-request-id", b"generic-error-request")],
            "query_string": b"",
            "server": ("testserver", 80),
            "scheme": "http",
            "client": ("testclient", 50000),
        }
    )

    response = asyncio.run(
        unhandled_exception_handler(
            request,
            RuntimeError("database password leaked here"),
        )
    )

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "generic-error-request"
    assert json.loads(response.body) == {
        "error": {
            "code": "internal_server_error",
            "message": "Internal server error",
            "details": None,
            "request_id": "generic-error-request",
        }
    }


def test_validation_error_uses_standardized_error_shape(client):
    response = client.post(
        "/applications",
        json={"company": "", "role_title": ""},
        headers={"X-Request-ID": "validation-request"},
    )

    assert_standard_error(
        response,
        code="validation_error",
        message="Request validation failed",
        status_code=422,
    )
    assert isinstance(response.json()["error"]["details"], list)
    assert response.json()["error"]["details"]


def test_unknown_route_uses_standardized_error_shape(client):
    response = client.get(
        "/not-a-real-route",
        headers={"X-Request-ID": "unknown-route-request"},
    )

    assert_standard_error(
        response,
        code="not_found",
        message="Not Found",
        status_code=404,
    )
    assert response.json()["error"]["details"] is None
