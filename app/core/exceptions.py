from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class FileTooLargeError(AppException):
    def __init__(self, message: str = "File is too large."):
        super().__init__(message, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


class UnsupportedFileTypeError(AppException):
    def __init__(self, message: str = "Unsupported file type."):
        super().__init__(message, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


class ProcessingError(AppException):
    def __init__(self, message: str = "Processing failed."):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


def register_exception_handlers(app):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @app.exception_handler(FileTooLargeError)
    async def file_too_large_handler(request: Request, exc: FileTooLargeError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @app.exception_handler(UnsupportedFileTypeError)
    async def unsupported_file_type_handler(request: Request, exc: UnsupportedFileTypeError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @app.exception_handler(ProcessingError)
    async def processing_error_handler(request: Request, exc: ProcessingError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )
