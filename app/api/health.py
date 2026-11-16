"""Health check endpoint."""

from fastapi import APIRouter

from app.config import settings
from app.schemas import HealthResponse

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Returns application health, version, and capability disclosure."""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        meter_engine="online",
        llm_configured=settings.is_llm_configured,
        environment=settings.ENV,
    )
