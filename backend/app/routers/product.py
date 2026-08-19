"""
Product analysis endpoints.

POST /api/v1/analyze — Core endpoint: accepts product info and returns enriched intelligence.

This router contains NO AI logic. It delegates all business logic to the
ProductService class. Reference: architecture_final.md §8.2 (Analyze Endpoint)
"""
import logging

from fastapi import APIRouter, HTTPException, status, Request
from slowapi.errors import RateLimitExceeded

from app.core.rate_limit import limiter
from app.core.config import settings
from app.schemas.request import ProductRequest
from app.schemas.response import ProductResponse
from app.services.product_service import ProductService
from app.services.gemini_service import GeminiServiceError

logger = logging.getLogger(__name__)

router = APIRouter()
product_service = ProductService()


@router.post(
    "/analyze",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze a product and generate intelligence",
    description=(
        "Accepts minimal product information (MPN, Brand, Description) and "
        "returns structured, commerce-ready product intelligence with "
        "confidence scores, validation report, and source attributions."
    ),
    responses={
        200: {"description": "Product intelligence generated successfully"},
        400: {"description": "Validation error in request body"},
        422: {"description": "Missing required fields or description too long"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(f"{settings.rate_limit_analyze}/minute")
async def analyze_product(
    request: Request,
    payload: ProductRequest,
) -> ProductResponse:
    """
    Analyze a product and generate structured intelligence.

    The endpoint validates the request via the Pydantic `ProductRequest`
    schema (enforcing required MPN, brand, and description fields with a
    1000-character description limit) and delegates all business logic to
    `ProductService.analyze()`.

    Args:
        request: The raw FastAPI request (used by the rate limiter).
        payload: Validated product information (mpn, brand, description).

    Returns:
        ProductResponse: Enriched product intelligence with confidence scores,
        validation report, sources, and agent timeline.

    Raises:
        HTTPException 422: If the payload fails validation.
        HTTPException 429: If the request rate limit is exceeded.
        HTTPException 500: If the service fails to process the request.
    """
    try:
        result = await product_service.analyze(payload)
    except RateLimitExceeded:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )
    except GeminiServiceError as exc:
        # Structured, typed error from the Gemini service layer:
        #   - Invalid/missing API key            -> 503
        #   - Network failure                    -> 503
        #   - Gemini rate limit                  -> 429
        #   - Empty AI response / invalid JSON   -> 502
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.to_dict(),
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected error during analysis", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis.",
        ) from exc

    return result

