"""
Document upload endpoints.

POST /api/v1/upload-document — Upload documents for RAG ingestion.

This router contains NO AI logic. It delegates all business logic to the
DocumentService class. Reference: architecture_final.md §8.2 (Upload Endpoint)
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, status

from app.core.rate_limit import limiter
from app.core.config import settings
from app.schemas.response import DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter()
document_service = DocumentService()


@router.post(
    "/upload-document",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a product document for RAG ingestion",
    description=(
        "Upload a technical document (PDF, TXT, CSV, or JSON) that will be "
        "processed for retrieval-augmented generation. The document is "
        "validated for type and size before processing."
    ),
    responses={
        201: {"description": "Document uploaded and processed"},
        400: {"description": "Invalid file type or empty file"},
        413: {"description": "File too large (max 10MB)"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(f"{settings.rate_limit_upload}/minute")
async def upload_document(
    request: Request,
    file: UploadFile = File(..., description="The document file to upload"),
    mpn: str = Form(None, description="Optional MPN to associate with the document"),
) -> DocumentUploadResponse:
    """
    Upload a technical document for RAG ingestion.

    Validates the file type (PDF/TXT/CSV/JSON) and size (max 10MB) before
    delegating processing to `DocumentService.upload()`.

    Args:
        request: The raw FastAPI request (used by the rate limiter).
        file: The uploaded document file.
        mpn: Optional MPN to associate with the document.

    Returns:
        DocumentUploadResponse: Document ID, processing status, and chunk count.

    Raises:
        HTTPException 400: If the file is empty or has an unsupported type.
        HTTPException 413: If the file exceeds the maximum upload size.
        HTTPException 429: If the request rate limit is exceeded.
    """
    # Reject oversized requests before buffering the multipart payload when the
    # client provided a usable content length.
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.max_upload_size_mb}MB.",
        )

    # Read in bounded chunks so chunked requests cannot exhaust memory.
    chunks = []
    size_bytes = 0
    while True:
        chunk = await file.read(min(1024 * 1024, max_bytes - size_bytes + 1))
        if not chunk:
            break
        chunks.append(chunk)
        size_bytes += len(chunk)
        if size_bytes > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {settings.max_upload_size_mb}MB.",
            )
    content = bytes().join(chunks)

    # An empty file is handled by DocumentService.

    try:
        result = await document_service.upload(
            filename=file.filename or "unnamed",
            content=content,
            size_bytes=size_bytes,
            mpn=mpn,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during upload: {exc}",
        ) from exc

    return DocumentUploadResponse(**result)

