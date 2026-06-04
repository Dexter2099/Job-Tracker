from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.middleware import REQUEST_ID_HEADER


def get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None) or request.headers.get(
        REQUEST_ID_HEADER
    )


def error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details=None,
) -> JSONResponse:
    request_id = get_request_id(request)
    response = JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "request_id": request_id,
            }
        },
    )
    if request_id is not None:
        response.headers[REQUEST_ID_HEADER] = request_id
    return response


def http_error_code(status_code: int) -> str:
    if status_code == 404:
        return "not_found"
    return "http_error"


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return error_response(
        request=request,
        status_code=exc.status_code,
        code=http_error_code(exc.status_code),
        message=message,
        details=None,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return error_response(
        request=request,
        status_code=422,
        code="validation_error",
        message="Request validation failed",
        details=exc.errors(),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return error_response(
        request=request,
        status_code=500,
        code="internal_server_error",
        message="Internal server error",
        details=None,
    )
