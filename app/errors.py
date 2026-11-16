from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ChhandAppError(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class InvalidMeterError(ChhandAppError):
    def __init__(
        self,
        message: str = "Invalid or unsupported meter specified.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="INVALID_METER",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class InvalidInputError(ChhandAppError):
    def __init__(
        self,
        message: str = "Input contains invalid or malformed data.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="INVALID_INPUT",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class InvalidCustomPatternError(ChhandAppError):
    def __init__(
        self,
        message: str = "Custom pattern must be a list of positive integers.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="INVALID_CUSTOM_PATTERN",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class LLMConfigurationError(ChhandAppError):
    def __init__(
        self,
        message: str = "LLM API key is not configured on this server.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="LLM_NOT_CONFIGURED",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details,
        )


class LLMTimeoutError(ChhandAppError):
    def __init__(
        self,
        message: str = "The LLM service timed out while generating suggestions.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="LLM_TIMEOUT",
            message=message,
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            details=details,
        )


class LLMProviderError(ChhandAppError):
    def __init__(
        self,
        message: str = "Error returned from LLM provider.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="LLM_PROVIDER_ERROR",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details,
        )


class NoVerifiedRewritesError(ChhandAppError):
    def __init__(
        self,
        message: str = "No candidates passed deterministic meter verification.",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            code="NO_VERIFIED_REWRITES",
            message=message,
            status_code=status.HTTP_200_OK,  # Returned as 200 with empty list according to spec
            details=details,
        )


def format_error_response(
    code: str, message: str, details: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Uniform error response structure."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }


def register_error_handlers(app: FastAPI) -> None:
    """Registers exception handlers on the FastAPI instance."""

    @app.exception_handler(ChhandAppError)
    async def app_error_handler(request: Request, exc: ChhandAppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=format_error_response(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        clean_errors = []
        for err in exc.errors():
            loc = " -> ".join(str(item) for item in err.get("loc", []))
            clean_errors.append(f"{loc}: {err.get('msg', 'validation error')}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=format_error_response(
                code="VALIDATION_ERROR",
                message="The request body did not pass validation.",
                details={"errors": clean_errors},
            ),
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
        # Never leak secrets or internal trace details
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred. Please try again.",
                details={},
            ),
        )
