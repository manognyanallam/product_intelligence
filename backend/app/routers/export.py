"""
Export endpoints.

GET /api/v1/download-json/{product_id} — Download analysis as JSON file.
GET /api/v1/download-pdf/{product_id}  — Download analysis as PDF report.

This router contains NO AI logic. It delegates all business logic to the
ExportService and ProductService classes.
Reference: architecture_final.md §8.2 (Export Endpoints)
"""
import json

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from app.core.rate_limit import limiter
from app.core.config import settings
from app.services.product_service import ProductService
from app.services.export_service import ExportService

router = APIRouter()
product_service = ProductService()
export_service = ExportService()


@router.get(
    "/download-json/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Download product intelligence as JSON",
    description="Downloads the structured product intelligence for a product as a JSON file.",
    responses={
        200: {"description": "JSON file download"},
        404: {"description": "Product not found"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(f"{settings.rate_limit_analyze}/minute")
async def download_json(
    request: Request,
    product_id: str,
):
    """
    Download structured product intelligence as a JSON file.

    Args:
        request: The raw FastAPI request (used by the rate limiter).
        product_id: The product analysis ID to export.

    Returns:
        StreamingResponse: JSON file download with Content-Disposition header.

    Raises:
        HTTPException 404: If the product is not found.
        HTTPException 429: If the request rate limit is exceeded.
    """
    product = await product_service.get_product(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found.",
        )

    # Serialize to JSON with indentation for readability.
    payload = product.model_dump()
    json_bytes = json.dumps(payload, indent=2, default=str).encode("utf-8")

    return StreamingResponse(
        iter([json_bytes]),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="product_{product_id}.json"'
        },
    )


@router.get(
    "/download-pdf/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Download product intelligence as PDF",
    description="Downloads a professional PDF report with all product intelligence data.",
    responses={
        200: {"description": "PDF report download"},
        404: {"description": "Product not found"},
        500: {"description": "PDF generation failed"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(f"{settings.rate_limit_analyze}/minute")
async def download_pdf(
    request: Request,
    product_id: str,
):
    """
    Download a professional PDF report with all product intelligence data.

    Args:
        request: The raw FastAPI request (used by the rate limiter).
        product_id: The product analysis ID to export.

    Returns:
        StreamingResponse: PDF file download with Content-Disposition header.

    Raises:
        HTTPException 404: If the product is not found.
        HTTPException 500: If PDF generation fails.
        HTTPException 429: If the request rate limit is exceeded.
    """
    product = await product_service.get_product(product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} not found.",
        )

    try:
        pdf_bytes = await export_service.generate_pdf(product)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {exc}",
        ) from exc

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="product_{product_id}.pdf"'
        },
    )

