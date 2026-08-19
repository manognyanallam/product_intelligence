"""
Domain models for the AI Product Intelligence Platform.

These are the core business entities used throughout the application.
They represent the internal data structures that flow through the multi-agent pipeline.
Reference: architecture_final.md §5 (Multi-Agent Design)
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class ProductRequest:
    """Input product information from the user."""
    mpn: str
    brand: str
    description: str
    options: Dict[str, Any] = field(default_factory=lambda: {"include_web_search": True, "confidence_threshold": 0.7})


@dataclass
class Document:
    """A retrieved document chunk with metadata."""
    id: str
    text: str
    metadata: Dict[str, Any]
    relevance_score: float = 0.0


@dataclass
class Source:
    """Source attribution for a piece of information."""
    source_id: str
    type: str  # datasheet, vector_db, knowledge_base
    name: str
    url: Optional[str] = None
    attributes_used: List[str] = field(default_factory=list)
    relevance_score: float = 0.0


@dataclass
class RetrievedContext:
    """Output of the Retrieval Agent — context for enrichment."""
    documents: List[Document] = field(default_factory=list)
    sources: List[Source] = field(default_factory=list)
    cache_hit: bool = False
    cached_result: Optional[Dict[str, Any]] = None
    relevance_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class EnrichedProduct:
    """Output of the Product Intelligence Agent — enriched product data."""
    title: str = ""
    description: str = ""
    specifications: Dict[str, Any] = field(default_factory=dict)
    applications: List[str] = field(default_factory=list)
    seo_keywords: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    category: str = ""
    alternate_parts: List[str] = field(default_factory=list)
    compliance: List[str] = field(default_factory=list)
    datasheet_url: Optional[str] = None


@dataclass
class ValidationCheck:
    """A single validation check for an attribute."""
    attribute: str
    status: str  # verified, partial, unverified, contradicted
    message: str = ""
    details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Output of the Validation & Confidence Agent."""
    overall_confidence: float = 0.0
    attribute_confidence: Dict[str, float] = field(default_factory=dict)
    validation_checks: List[ValidationCheck] = field(default_factory=list)
    source_attributions: List[Source] = field(default_factory=list)
    status: str = "passed"  # passed, partial, failed


@dataclass
class AgentTimelineEntry:
    """A single entry in the agent processing timeline."""
    agent: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: str = "pending"


@dataclass
class AgentContext:
    """Shared context object passed through the multi-agent pipeline."""
    request_id: str
    input: ProductRequest
    status: str = "processing"
    current_agent: str = "retrieval"
    retrieval: Optional[RetrievedContext] = None
    enrichment: Optional[EnrichedProduct] = None
    validation: Optional[ValidationResult] = None
    errors: List[str] = field(default_factory=list)
    timeline: List[AgentTimelineEntry] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
