"""
Product Intelligence Agent — Agent 2 of the Multi-Agent System.

Responsibilities:
- Generate product Title (e.g., "SN74LS00N Quad 2-Input Positive-NAND Gate IC")
- Generate detailed, SEO-optimized Description (2-3 paragraphs)
- Generate structured Specifications table
- Identify primary and secondary Applications
- Generate SEO Keywords for e-commerce discovery
- Identify key product Features
- Assign hierarchical Category
- Output EnrichedProduct

Reference: architecture_final.md §5.3 (Agent 2: Product Intelligence Agent)
"""
import json
from typing import Optional
from app.agents.base_agent import BaseAgent
from app.models.domain import ProductRequest, RetrievedContext, EnrichedProduct


class ProductIntelligenceAgent(BaseAgent):
    """
    Agent responsible for generating structured product intelligence.

    Uses Gemini via LangChain to generate all product attributes.
    The generation is grounded in the retrieved context to reduce hallucinations.
    """

    def __init__(self):
        """Initialize the Product Intelligence Agent."""
        super().__init__(agent_name="Product Intelligence Agent")
        # TODO: Initialize LangChain components
        #   - ChatGemini (gemini-3.1-flash-lite)
        #   - Prompt templates
        #   - Structured output parser
        #   - RunnableSequence

    async def run(
        self, input: ProductRequest, context: Optional[RetrievedContext] = None
    ) -> EnrichedProduct:
        """
        Execute the product intelligence generation process.

        Steps:
        1. Construct augmented prompt with system instructions, context, and query
        2. Invoke Gemini via LangChain chain
        3. Parse structured JSON output
        4. Validate all required fields
        5. Retry on parse failure (temperature=0.3)
        6. Return EnrichedProduct

        Args:
            input: The product request with MPN, brand, and description
            context: Retrieved context from the Retrieval Agent

        Returns:
            EnrichedProduct with all generated attributes
        """
        self.log_start(f"Generating intelligence for {input.mpn}")

        prompt = self._build_prompt(input, context)
        try:
            from app.services.gemini_service import GeminiService
            response = await GeminiService()._invoke_gemini(prompt)
            return self._parse_response(response)
        except (ValueError, json.JSONDecodeError):
            raise
        except Exception as exc:
            self.log_error("product intelligence generation", exc)
            raise

    def _build_prompt(self, input: ProductRequest, context: Optional[RetrievedContext]) -> str:
        """
        Build the augmented prompt for Gemini.

        Includes:
        - System instruction (role, task, output format)
        - Retrieved context (documents with relevance scores)
        - Few-shot examples (3 example enrichments)
        - User query (MPN, Brand, Description)

        Args:
            input: Product request data
            context: Retrieved context for grounding

        Returns:
            Formatted prompt string
        """
        context_text = "\n".join(doc.text for doc in (context.documents if context else []))
        return (
            "Generate product intelligence as JSON with title, description, "
            "specifications, applications, seo_keywords, features, category.\n"
            f"MPN: {input.mpn}\nBrand: {input.brand}\nDescription: {input.description}\n"
            f"Reference context:\n{context_text}"
        )

    def _parse_response(self, response: str) -> EnrichedProduct:
        """
        Parse the Gemini response into an EnrichedProduct.

        Args:
            response: Raw JSON string from Gemini

        Returns:
            Parsed EnrichedProduct

        Raises:
            ValueError: If JSON parsing fails or required fields are missing
        """
        data = json.loads(response)
        if not isinstance(data, dict):
            raise ValueError("Gemini response must be a JSON object")
        required = ("title", "description", "specifications", "applications", "seo_keywords", "features", "category")
        missing = [field for field in required if field not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        return EnrichedProduct(
            title=data["title"], description=data["description"],
            specifications=data["specifications"], applications=data["applications"],
            seo_keywords=data["seo_keywords"], features=data["features"], category=data["category"],
        )
