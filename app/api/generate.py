"""AI poetry generation endpoint."""

from fastapi import APIRouter, HTTPException

from app.errors import (
    GeminiAuthError,
    GeminiNotConfiguredError,
    GeminiProviderError,
    GeminiRateLimitError,
    GeminiTimeoutError,
)
from app.poetry.generator import generate_poem
from app.schemas import GenerateRequest, GenerateResponse

router = APIRouter(tags=["Poetry Generation"])


@router.post("/generate", response_model=GenerateResponse)
async def generate_poetry_endpoint(request: GenerateRequest) -> GenerateResponse:
    """Generate original poetry in Hindi, Urdu, or Bengali with meter verification."""
    try:
        return await generate_poem(request)
    except GeminiNotConfiguredError as exc:
        raise HTTPException(
            status_code=503,
            detail={"code": "GEMINI_NOT_CONFIGURED", "message": str(exc)},
        ) from exc
    except GeminiAuthError as exc:
        raise HTTPException(
            status_code=401,
            detail={"code": "GEMINI_AUTH_ERROR", "message": str(exc)},
        ) from exc
    except GeminiRateLimitError as exc:
        raise HTTPException(
            status_code=429,
            detail={"code": "GEMINI_RATE_LIMIT", "message": str(exc)},
        ) from exc
    except GeminiTimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail={"code": "GEMINI_TIMEOUT", "message": str(exc)},
        ) from exc
    except GeminiProviderError as exc:
        raise HTTPException(
            status_code=502,
            detail={"code": "GEMINI_PROVIDER_ERROR", "message": str(exc)},
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
