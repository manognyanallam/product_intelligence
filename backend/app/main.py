"""
AI Product Intelligence Platform — FastAPI Application Entry Point

Initializes the FastAPI application with:
- CORS middleware
- Structured logging
- Global exception handlers
- Rate limiting
- Routers for all API endpoints

Reference: architecture_final.md §3 (System Architecture), §12 (Security)

Endpoints (defined in routers/):
    POST /api/v1/analyze            — Analyze product and generate intelligence
    POST /api/v1/upload-document    — Upload product document for RAG
    GET  /api/v1/history            — Get analysis history
    GET  /api/v1/health             — Health check
    GET  /api/v1/download-json/{id} — Download JSON export
    GET  /api/v1/download-pdf/{id}  — Download PDF report
"""
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.rate_limit import limiter
from app.routers import product, document, history, health, export, evaluation

# Configure structured logging.
from app.utils.logger import setup_logging
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Application factory for the AI Product Intelligence Platform.

    Builds the FastAPI application with middleware, exception handlers,
    and routers.

    Returns:
        FastAPI: The configured application instance.
    """
    app = FastAPI(
        title="AI Product Intelligence Platform API",
        description=(
            "Turn minimal product data — MPN, Brand, and Description — into "
            "rich, structured, validated, commerce-ready product intelligence. "
            "Built for UniHack by Unilog."
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {"name": "Product", "description": "Product analysis endpoints"},
            {"name": "Document", "description": "Document upload endpoints"},
            {"name": "History", "description": "Analysis history endpoints"},
            {"name": "Export", "description": "Export endpoints (JSON/PDF)"},
            {"name": "Health", "description": "Health check endpoint"},
        ],
    )

    # --- Rate limiting ----------------------------------------------------
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # --- CORS -------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Global exception handlers ----------------------------------------
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Global handler for unhandled exceptions.

        Logs the error and returns a generic 500 response to avoid leaking
        internal details to clients.

        Args:
            request: The failing request.
            exc: The unhandled exception.

        Returns:
            JSONResponse: A 500 Internal Server Error response.
        """
        logger.exception(
            "Unhandled exception on %s %s",
            request.method,
            request.url.path,
            exc_info=exc,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred."},
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        """
        Handler for rate limit exceeded errors.

        Args:
            request: The failing request.
            exc: The rate limit exception.

        Returns:
            JSONResponse: A 429 Too Many Requests response.
        """
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "limit": str(exc.detail),
            },
        )

    # --- Request timing middleware ----------------------------------------
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """
        Middleware that measures request processing time and logs each request.

        Args:
            request: The incoming request.
            call_next: The next middleware/handler in the chain.

        Returns:
            Response: The response with an X-Process-Time header added.
        """
        start = time.perf_counter()
        response = await call_next(request)
        process_time = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time-MS"] = f"{process_time:.2f}"
        logger.info(
            "Request %s %s -> %s (%dms)",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )
        return response

    # --- Routers -----------------------------------------------------------
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(product.router, prefix="/api/v1")
    app.include_router(document.router, prefix="/api/v1")
    app.include_router(history.router, prefix="/api/v1")
    app.include_router(export.router, prefix="/api/v1")
    app.include_router(evaluation.router, prefix="/api/v1")

    # --- Root endpoint ------------------------------------------------------
    @app.get("/", tags=["Info"], include_in_schema=False)
    async def root():
        """
        Root endpoint with API information.

        Returns:
            dict: API metadata and link to documentation.
        """
        return {
            "name": "AI Product Intelligence Platform API",
            "version": "2.0.0",
            "docs": "/docs",
            "health": "/api/v1/health",
            "event": "UniHack by Unilog 2025",
        }

    return app


app = create_app()

