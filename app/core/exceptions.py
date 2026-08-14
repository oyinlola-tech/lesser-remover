"""Unified error format and exception handling.

Every API error is returned as::

    {
        "error": {
            "code": "FILE_TOO_LARGE",
            "message": "human readable message",
            "request_id": "abc123...",
            "status": 413
        }
    }

Responses never expose stack traces, filesystem paths, secrets,
environment variables, or internal tokens.
"""

import logging
import uuid

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_ERROR",
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message)


class FileTooLargeError(AppException):
    def __init__(
        self,
        message: str = "File is too large.",
        code: str = "FILE_TOO_LARGE",
    ):
        super().__init__(
            message,
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            code,
        )


class UnsupportedFileTypeError(AppException):
    def __init__(
        self,
        message: str = "Unsupported file type.",
        code: str = "UNSUPPORTED_FILE_TYPE",
    ):
        super().__init__(
            message,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            code,
        )


class ProcessingError(AppException):
    def __init__(
        self,
        message: str = "Processing failed.",
        code: str = "PROCESSING_FAILED",
    ):
        super().__init__(
            message,
            status.HTTP_400_BAD_REQUEST,
            code,
        )


class NotFoundError(AppException):
    def __init__(
        self,
        message: str = "Resource not found.",
        code: str = "NOT_FOUND",
    ):
        super().__init__(
            message,
            status.HTTP_404_NOT_FOUND,
            code,
        )


class InvalidRequestError(AppException):
    def __init__(
        self,
        message: str = "Invalid request.",
        code: str = "INVALID_REQUEST",
    ):
        super().__init__(
            message,
            status.HTTP_400_BAD_REQUEST,
            code,
        )


def _error_payload(
    request: Request,
    code: str,
    message: str,
    status_code: int,
) -> dict:
    request_id = getattr(request.state, "request_id", None)
    if not request_id:
        request_id = uuid.uuid4().hex
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
            "status": status_code,
        }
    }


def register_exception_handlers(app) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                request,
                exc.code,
                exc.message,
                exc.status_code,
            ),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ):
        code_map = {
            status.HTTP_404_NOT_FOUND: "NOT_FOUND",
            status.HTTP_400_BAD_REQUEST: "INVALID_REQUEST",
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: "FILE_TOO_LARGE",
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: (
                "UNSUPPORTED_FILE_TYPE"
            ),
        }
        code = code_map.get(exc.status_code, "REQUEST_ERROR")
        message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                request,
                code,
                message,
                exc.status_code,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ):
        return await http_exception_handler(request, exc)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        message = "Invalid request parameters."
        try:
            first = exc.errors()[0]
            field = ".".join(
                str(part) for part in first.get("loc", [])
            )
            message = (
                f"Invalid value for '{field}': "
                f"{first.get('msg', 'validation error')}"
            )
        except (IndexError, KeyError, TypeError):
            pass
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_payload(
                request,
                "VALIDATION_ERROR",
                message,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ):
        logger.exception(
            "Unhandled error on %s %s",
            request.method,
            request.url.path,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(
                request,
                "INTERNAL_ERROR",
                "An unexpected error occurred. Please try again.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
        )
