"""
Product Service — Orchestrates the pipeline for product intelligence generation.

This phase implements the Gemini integration: the service invokes the
GeminiService to generate real, AI-powered product intelligence from the
minimal MPN / Brand / Description input.

Reference: architecture_final.md §5.3 (Agent 2: Product Intelligence Agent),
§8.2 (Analyze Endpoint), §11 (Workflow)
"""
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from app.schemas.request import ProductRequest
from app.schemas.response import (
    ProductResponse, ProductInput, EnrichedData, ConfidenceScore,
    ValidationReport, ValidationCheck, Source, AgentTimeline,
)
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class ProductService:
    """
    Business logic for product analysis.

    Orchestrates AI product intelligence generation via Google Gemini.
    """

    # Class-level shared store so every ProductService instance (across routers)
    # sees the same analyzed products. This mirrors the eventual ChromaDB-backed
    # persistence where data is shared across the whole application.
    _store: Dict[str, ProductResponse] = {}

    def __init__(self, gemini_service: Optional[GeminiService] = None) -> None:
        """Initialize the product service with a Gemini service."""
        # In-memory store of analyzed products for the history endpoint.
        # Uses the shared class-level dict so lookups work across router instances.
        self._store = ProductService._store
        self._gemini = gemini_service or GeminiService()

    async def analyze(self, request: ProductRequest) -> ProductResponse:
        """
        Analyze a product and generate structured intelligence.

        Invokes Gemini to generate the product title, category, description,
        features, technical specifications, applications, SEO keywords, and a
        confidence reason. Results are mapped into the standard ProductResponse.

        Args:
            request: Validated product request (mpn, brand, description).

        Returns:
            ProductResponse: AI-generated enriched product intelligence.

        Raises:
            GeminiServiceError: If Gemini generation fails (invalid key,
                network error, rate limit, empty/invalid response).
        """
        product_id = f"prod_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()

        started = time.perf_counter()
        logger.info(
            "Starting product analysis: product_id=%s mpn=%s brand=%s",
            product_id,
            request.mpn,
            request.brand,
        )

        # 1. Generate product intelligence via Gemini.
        ai = await self._gemini.generate_product_intelligence(
            mpn=request.mpn,
            brand=request.brand,
            description=request.description,
        )
        elapsed_ms = int((time.perf_counter() - started) * 1000)

        # 2. Map the AI output into the response schema.
        enriched = self._build_enriched_data(request, ai)
        technical_specs = enriched.specifications
        features = enriched.features
        applications = enriched.applications
        seo_keywords = enriched.seo_keywords
        title = enriched.title
        category = enriched.category
        description = enriched.description

        # 3. Build confidence scores.
        confidence = self._build_confidence(enriched)
        overall = confidence.overall
        # 4. Build validation report.
        validation = self._build_validation_report(enriched)

        # 5. Add source attribution and agent timeline.
        sources = self._build_sources()
        agent_timeline = self._build_agent_timeline(elapsed_ms)

        # 6. Build the final response.
        response = self._build_response(
            product_id=product_id,
            request=request,
            enriched=enriched,
            confidence=confidence,
            validation=validation,
            sources=sources,
            agent_timeline=agent_timeline,
            created_at=now,
        )

        # Cache in memory for history/export lookups.
        self._store[product_id] = response

        logger.info(
            "Product analysis completed: product_id=%s mpn=%s duration_ms=%d confidence=%s",
            product_id,
            request.mpn,
            elapsed_ms,
            overall,
        )
        return response

    @staticmethod
    def _build_validation_report(enriched: EnrichedData) -> ValidationReport:
        checks = [
            ValidationCheck(
                attribute="mpn", status="verified",
                message="MPN taken from validated input.",
            ),
            ValidationCheck(
                attribute="brand", status="verified",
                message="Brand taken from validated input.",
            ),
            ValidationCheck(
                attribute="category",
                status="verified" if enriched.category else "unverified",
                message=("Category generated by Gemini." if enriched.category
                         else "Gemini did not return a category."),
            ),
            ValidationCheck(
                attribute="specifications",
                status="verified" if enriched.specifications else "unverified",
                message=(
                    f"Gemini returned {len(enriched.specifications)} specifications."
                    if enriched.specifications
                    else "Gemini did not return specifications."
                ),
            ),
            ValidationCheck(
                attribute="title",
                status="verified" if enriched.title else "unverified",
                message=("Title generated by Gemini." if enriched.title
                         else "Gemini did not return a title."),
            ),
        ]
        issues = []
        if not enriched.category:
            issues.append("Gemini did not generate a category.")
        if not enriched.specifications:
            issues.append("Gemini did not generate technical specifications.")
        return ValidationReport(
            status="passed" if not issues else "partial",
            checks=checks,
            issues=issues,
        )

    def _build_sources(self) -> list[Source]:
        return [
            Source(
                source_id="src_gemini_001",
                type="knowledge_base",
                name=f"Google Gemini ({self._gemini.model})",
                attributes_used=[
                    "title", "category", "description", "specifications",
                    "features", "applications", "seo_keywords",
                ],
                relevance_score=0.75,
            )
        ]

    @staticmethod
    def _build_agent_timeline(elapsed_ms: int) -> list[AgentTimeline]:
        return [
            AgentTimeline(agent="retrieval", status="skipped", duration_ms=0),
            AgentTimeline(agent="intelligence", status="completed", duration_ms=elapsed_ms),
            AgentTimeline(agent="validation", status="skipped", duration_ms=0),
        ]

    @staticmethod
    def _build_response(
        product_id: str,
        request: ProductRequest,
        enriched: EnrichedData,
        confidence: ConfidenceScore,
        validation: ValidationReport,
        sources: list[Source],
        agent_timeline: list[AgentTimeline],
        created_at: str,
    ) -> ProductResponse:
        return ProductResponse(
            product_id=product_id,
            status="completed",
            input=ProductInput(
                mpn=request.mpn,
                brand=request.brand,
                description=request.description,
            ),
            enriched_data=enriched,
            confidence=confidence,
            validation=validation,
            sources=sources,
            agent_timeline=agent_timeline,
            created_at=created_at,
        )

    @staticmethod
    def _build_enriched_data(request: ProductRequest, ai: Dict[str, Any]) -> EnrichedData:
        ""Map only values with the expected shape into the response model."""
        def text_value(key: str) -> str:
            value = ai.get(key, "")
            return value if isinstance(value, str) else ""

        def string_list(key: str) -> list[str]:
            value = ai.get(key, [])
            return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []

        specifications = ai.get("technical_specifications", {})
        if not isinstance(specifications, dict):
            specifications = {}
        specifications = {
            str(key): value
            for key, value in specifications.items()
            if isinstance(value, (str, int, float, bool))
        }
        description = text_value("description")
        return EnrichedData(
            mpn=request.mpn,
            brand=request.brand,
            manufacturer=request.brand,
            category=text_value("category"),
            title=text_value("title"),
            description=description,
            long_description=description,
            specifications=specifications,
            features=string_list("key_features"),
            applications=string_list("applications"),
            seo_keywords=string_list("seo_keywords"),
            compliance=[],
            alternate_parts=[],
            datasheet_url=None,
        )

    @staticmethod
    def _build_confidence(enriched: EnrichedData) -> ConfidenceScore:
        attributes = {
            "mpn": 1.0, "brand": 1.0,
            "description": 0.7 if enriched.description else 0.0,
            "category": 0.6 if enriched.category else 0.0,
            "title": 0.7 if enriched.title else 0.0,
            "specifications": 0.6 if enriched.specifications else 0.0,
            "features": 0.6 if enriched.features else 0.0,
            "applications": 0.6 if enriched.applications else 0.0,
            "seo_keywords": 0.6 if enriched.seo_keywords else 0.0,
        }
        overall = round(sum(attributes.values()) / len(attributes), 4)
        return ConfidenceScore(overall=overall, attributes=attributes)

    async def get_product(self, product_id: str) -> ProductResponse | None:
        """
        Retrieve a previously analyzed product by ID.

        Args:
            product_id: The product analysis ID.

        Returns:
            The stored ProductResponse or None if not found.
        """
        return self._store.get(product_id)

