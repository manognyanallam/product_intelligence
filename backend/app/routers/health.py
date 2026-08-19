"""
Health check endpoint.

GET /api/v1/health — Returns the health status of the application and its dependencies.

Reference: architecture_final.md §8.2 (Health Endpoint)
"""
import time

from fastapi import APIRouter, Request, status

from app.core.rate_limit import limiter
from app.core.config import settings
from app.schemas.response import HealthResponse

router = APIRouter()

# Application start time used to compute uptime.
_START_TIME = time.time()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Returns the health status of the application, version, uptime, and dependency status.",
    responses={
        200: {"description": "Application is healthy"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(f"{settings.rate_limit_health}/minute")
async def health_check(
    request: Request,
) -> HealthResponse:
    """
    Health check endpoint for monitoring and deployment verification.

    Returns the application status, version, uptime, and dependency status.

    Args:
        request: The raw FastAPI request (used by the rate limiter).

    Returns:
        HealthResponse: Application health status.
    """
    uptime_seconds = int(time.time() - _START_TIME)

    # Report Gemini configuration status without validating the key (which
    # would trigger a network call). A configured key => "configured".
    gemini_status = "configured" if settings.gemini_api_key else "not_configured"

    return HealthResponse(
        status="healthy",
        version="2.0.0",
        uptime=uptime_seconds,
        chromadb="not_configured",  # Real check implemented in a later phase.
        gemini=gemini_status,
    )

