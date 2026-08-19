"""
Validation & Confidence Agent — Agent 3 of the Multi-Agent System.

Responsibilities:
- Validate every generated attribute against retrieved context
- Compare attributes with source documents
- Detect hallucinations (attributes not supported by any source)
- Generate per-attribute confidence scores (0.0 – 1.0)
- Calculate overall confidence score
- Generate detailed validation report
- Generate source attribution for every attribute
- Output ValidationResult

Reference: architecture_final.md §5.4 (Agent 3: Validation & Confidence Agent)
"""
from typing import Any, Optional
from app.agents.base_agent import BaseAgent
from app.models.domain import (
    EnrichedProduct, RetrievedContext, ValidationResult,
    ValidationCheck, Source
)


class ValidationConfidenceAgent(BaseAgent):
    """
    Agent responsible for validating generated data and assigning confidence scores.

    Uses a combination of:
    - LLM-based validation (Gemini comparison chain)
    - Rule-based validation (regex, pattern matching)
    - Statistical confidence scoring
    """

    def __init__(self):
        """Initialize the Validation & Confidence Agent."""
        super().__init__(agent_name="Validation & Confidence Agent")
        # TODO: Initialize validation components
        #   - Gemini comparison chain
        #   - Rule-based validators
        #   - Confidence scoring calculator

    async def run(
        self, enriched: EnrichedProduct, context: Optional[RetrievedContext] = None
    ) -> ValidationResult:
        """
        Execute the validation and confidence scoring process.

        Steps:
        1. For each attribute in EnrichedProduct:
           a. Search context for supporting evidence
           b. Check for contradictions
           c. Assign verification status
           d. Calculate attribute confidence score
           e. Map to source documents
        2. Calculate overall confidence (weighted average)
        3. Generate validation report
        4. Generate source attribution
        5. Return ValidationResult

        Args:
            enriched: The enriched product data to validate
            context: Retrieved context for comparison

        Returns:
            ValidationResult with scores, report, and source attributions
        """
        self.log_start("Validating generated product intelligence")

        values = {name: value for name, value in vars(enriched).items() if value not in (None, "", [], {})}
        active_context = context or RetrievedContext()
        checks = [self._check_hallucination(name, value, active_context) for name, value in values.items()]
        scores = {check.attribute: self._calculate_confidence(check.attribute, values[check.attribute], active_context) for check in checks}
        sources = active_context.sources
        overall = self._calculate_overall_confidence(scores)
        status = "failed" if any(check.status == "contradicted" for check in checks) else ("partial" if any(check.status == "unverified" for check in checks) else "passed")
        return ValidationResult(overall_confidence=overall, attribute_confidence=scores, validation_checks=checks, source_attributions=sources, status=status)

    def _calculate_confidence(
        self, attribute: str, value: Any, context: RetrievedContext
    ) -> float:
        """
        Calculate confidence score for a single attribute.

        Formula:
            confidence = 0.35 × source_support + 0.25 × validation_status
                       + 0.20 × source_count     + 0.10 × consistency
                       + 0.10 × attribute_type_boost

        Where:
            source_support    = proportion of attribute confirmed by sources
            validation_status = 1.0 (verified), 0.5 (partial), 0.0 (unverified)
            source_count      = min(source_count / 3, 1.0)
            consistency       = internal consistency check score
            attribute_type_boost = 0.1 for MPN/Brand, 0 for others

        Args:
            attribute: Attribute name
            value: Attribute value
            context: Retrieved context for comparison

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not context.documents:
            return 0.0
        text = " ".join(document.text.lower() for document in context.documents)
        value_text = str(value).lower()
        support = 1.0 if value_text and value_text in text else 0.0
        source_count = min(len(context.documents) / 3, 1.0)
        return round(0.35 * support + 0.25 * support + 0.20 * source_count + 0.10 * support + (0.10 if attribute in {"mpn", "brand"} else 0.0), 4)

    def _check_hallucination(
        self, attribute: str, value: Any, context: RetrievedContext
    ) -> ValidationCheck:
        """
        Check if an attribute value is hallucinated (not supported by any source).

        Args:
            attribute: Attribute name
            value: Attribute value
            context: Retrieved context

        Returns:
            ValidationCheck with status and message
        """
        if not context.documents:
            return ValidationCheck(attribute=attribute, status="unverified", message="No source documents available.")
        supported = str(value).lower() in " ".join(document.text.lower() for document in context.documents)
        return ValidationCheck(attribute=attribute, status="verified" if supported else "unverified", message="Value found in source context." if supported else "No supporting evidence found.")

    def _calculate_overall_confidence(self, scores: dict) -> float:
        """
        Calculate overall confidence from per-attribute scores.

        Uses weighted average where critical attributes (MPN, Brand) have
        higher weight than generated attributes.

        Args:
            scores: Dictionary of attribute → confidence score

        Returns:
            Overall confidence score between 0.0 and 1.0
        """
        if not scores:
            return 0.0

        # Critical attributes get higher weight
        weights = {
            'mpn': 0.20, 'brand': 0.15, 'category': 0.10,
            'title': 0.10, 'description': 0.10, 'specifications': 0.15,
            'features': 0.05, 'applications': 0.05, 'seo_keywords': 0.05,
            'compliance': 0.05,
        }

        total_weight = 0.0
        weighted_sum = 0.0

        for attr, score in scores.items():
            w = weights.get(attr, 0.05)
            weighted_sum += score * w
            total_weight += w

        return weighted_sum / total_weight if total_weight > 0 else 0.0
