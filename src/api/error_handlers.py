"""
Error handlers for the FastAPI application
"""

import logging
from typing import Union

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from .models import ErrorResponse

logger = logging.getLogger(__name__)


def create_error_handlers(app: FastAPI) -> None:
    """
    Create and register error handlers for the FastAPI application
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """
        Handle HTTP exceptions
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            f"HTTP exception - {request_id} - "
            f"Status: {exc.status_code} - "
            f"Detail: {exc.detail} - "
            f"Path: {request.url.path}"
        )

        error_response = ErrorResponse(
            error="http_error",
            message=str(exc.detail),
            details={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict(),
            headers=exc.headers,
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """
        Handle Starlette HTTP exceptions
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            f"Starlette HTTP exception - {request_id} - "
            f"Status: {exc.status_code} - "
            f"Detail: {exc.detail} - "
            f"Path: {request.url.path}"
        )

        error_response = ErrorResponse(
            error="http_error",
            message=str(exc.detail),
            details={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.dict(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
        Handle request validation errors
        """
        request_id = getattr(request.state, "request_id", "unknown")

        # Extract validation error details
        error_details = []
        for error in exc.errors():
            error_details.append({
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
                "input": error.get("input"),
            })

        logger.warning(
            f"Validation error - {request_id} - "
            f"Path: {request.url.path} - "
            f"Errors: {len(error_details)}"
        )

        error_response = ErrorResponse(
            error="validation_error",
            message="Request validation failed",
            details={
                "validation_errors": error_details,
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict(),
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            f"Pydantic validation error - {request_id} - "
            f"Path: {request.url.path} - "
            f"Error: {str(exc)}"
        )

        error_response = ErrorResponse(
            error="validation_error",
            message="Data validation failed",
            details={
                "validation_error": str(exc),
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.dict(),
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exception_handler(
        request: Request, exc: RateLimitExceeded
    ) -> JSONResponse:
        """
        Handle rate limit exceeded errors
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            f"Rate limit exceeded - {request_id} - "
            f"Path: {request.url.path} - "
            f"Detail: {exc.detail}"
        )

        error_response = ErrorResponse(
            error="rate_limit_exceeded",
            message="Rate limit exceeded",
            details={
                "retry_after": getattr(exc, "retry_after", None),
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
                "limit_detail": exc.detail,
            },
        )

        headers = {}
        if hasattr(exc, "retry_after"):
            headers["Retry-After"] = str(exc.retry_after)

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=error_response.dict(),
            headers=headers,
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """
        Handle ValueError exceptions
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            f"Value error - {request_id} - "
            f"Path: {request.url.path} - "
            f"Error: {str(exc)}"
        )

        error_response = ErrorResponse(
            error="value_error",
            message="Invalid value provided",
            details={
                "error_detail": str(exc),
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.dict(),
        )

    @app.exception_handler(FileNotFoundError)
    async def file_not_found_error_handler(
        request: Request, exc: FileNotFoundError
    ) -> JSONResponse:
        """
        Handle FileNotFoundError exceptions
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            f"File not found error - {request_id} - "
            f"Path: {request.url.path} - "
            f"Error: {str(exc)}"
        )

        error_response = ErrorResponse(
            error="file_not_found",
            message="Required file not found",
            details={
                "error_detail": str(exc),
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response.dict(),
        )

    @app.exception_handler(PermissionError)
    async def permission_error_handler(
        request: Request, exc: PermissionError
    ) -> JSONResponse:
        """
        Handle PermissionError exceptions
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            f"Permission error - {request_id} - "
            f"Path: {request.url.path} - "
            f"Error: {str(exc)}"
        )

        error_response = ErrorResponse(
            error="permission_denied",
            message="Permission denied",
            details={
                "error_detail": str(exc),
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response.dict(),
        )

    @app.exception_handler(ConnectionError)
    async def connection_error_handler(
        request: Request, exc: ConnectionError
    ) -> JSONResponse:
        """
        Handle ConnectionError exceptions
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            f"Connection error - {request_id} - "
            f"Path: {request.url.path} - "
            f"Error: {str(exc)}"
        )

        error_response = ErrorResponse(
            error="connection_error",
            message="Connection failed",
            details={
                "error_detail": str(exc),
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response.dict(),
        )

    @app.exception_handler(TimeoutError)
    async def timeout_error_handler(request: Request, exc: TimeoutError) -> JSONResponse:
        """
        Handle TimeoutError exceptions
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            f"Timeout error - {request_id} - "
            f"Path: {request.url.path} - "
            f"Error: {str(exc)}"
        )

        error_response = ErrorResponse(
            error="timeout_error",
            message="Request timeout",
            details={
                "error_detail": str(exc),
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            },
        )

        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content=error_response.dict(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Handle all other exceptions
        """
        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            f"Unhandled exception - {request_id} - "
            f"Path: {request.url.path} - "
            f"Error: {str(exc)} - "
            f"Type: {type(exc).__name__}",
            exc_info=True
        )

        error_response = ErrorResponse(
            error="internal_server_error",
            message="An unexpected error occurred",
            details={
                "error_type": type(exc).__name__,
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
                # Don't expose internal error details in production
                "error_detail": str(exc) if app.debug else "Internal server error",
            },
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.dict(),
        )


# Custom exception classes
class RAGSystemError(Exception):
    """
    Custom exception for RAG system errors
    """

    def __init__(self, message: str, error_code: str = "rag_error", details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseError(RAGSystemError):
    """
    Custom exception for database-related errors
    """

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "database_error", details)


class AuthenticationError(RAGSystemError):
    """
    Custom exception for authentication errors
    """

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "authentication_error", details)


class AuthorizationError(RAGSystemError):
    """
    Custom exception for authorization errors
    """

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "authorization_error", details)


class ConfigurationError(RAGSystemError):
    """
    Custom exception for configuration errors
    """

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "configuration_error", details)


# Error response helpers
def create_error_response(
    error_type: str,
    message: str,
    status_code: int = 500,
    details: dict = None,
    request_id: str = None,
) -> JSONResponse:
    """
    Create a standardized error response
    """
    error_response = ErrorResponse(
        error=error_type,
        message=message,
        details=details or {},
    )

    if request_id:
        error_response.details["request_id"] = request_id

    return JSONResponse(
        status_code=status_code,
        content=error_response.dict(),
    )


def handle_rag_system_error(exc: RAGSystemError, request_id: str = None) -> JSONResponse:
    """
    Handle custom RAG system errors
    """
    status_codes = {
        "rag_error": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "database_error": status.HTTP_503_SERVICE_UNAVAILABLE,
        "authentication_error": status.HTTP_401_UNAUTHORIZED,
        "authorization_error": status.HTTP_403_FORBIDDEN,
        "configuration_error": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    status_code = status_codes.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    details = exc.details.copy() if exc.details else {}
    if request_id:
        details["request_id"] = request_id

    return create_error_response(
        error_type=exc.error_code,
        message=exc.message,
        status_code=status_code,
        details=details,
    )