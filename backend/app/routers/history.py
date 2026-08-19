"""
History endpoints.

GET /api/v1/history — Retrieve paginated analysis history.

This router contains NO AI logic. It delegates all business logic to the
HistoryService class. Reference: architecture_final.md §8.2 (History Endpoint)
"""
from fastapi import APIRouter, Query, HTTPException, Request, status

from app.core.rate_limit import limiter
from app.core.config import settings
from app.schemas.response import HistoryResponse
from app.services.history_service import HistoryService

router = APIRouter()
history_service = HistoryService()


@router.get(
    "/history",
    response_model=HistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve product analysis history",
    description=(
        "Returns a paginated list of previously analyzed products, sorted by "
        "analysis timestamp."
    ),
    responses={
        200: {"description": "History retrieved successfully"},
        400: {"description": "Invalid query parameters"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(f"{settings.rate_limit_history}/minute")
async def get_history(
    request: Request,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    sort: str = Query("desc", pattern="^(asc|desc)$", description="Sort order by timestamp"),
) -> HistoryResponse:
    """
    Retrieve paginated analysis history.

    Args:
        request: The raw FastAPI request (used by the rate limiter).
        page: Page number (1-indexed).
        limit: Number of items per page (max 100).
        sort: Sort order by timestamp: "asc" or "desc".

    Returns:
        HistoryResponse: Paginated history entries with total count.

    Raises:
        HTTPException 400: If query parameters are invalid.
        HTTPException 429: If the request rate limit is exceeded.
    """
    try:
        result = await history_service.get_history(page=page, limit=limit, sort=sort)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching history: {exc}",
        ) from exc

    return result

