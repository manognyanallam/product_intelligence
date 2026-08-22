"""
Gemini Service ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Google Generative AI integration for product intelligence.

Responsibilities:
- Read GEMINI_API_KEY securely from settings (loaded from .env)
- Invoke Gemini via the official Google Generative AI Python SDK (`google-genai`)
- Generate structured product intelligence as strict JSON only
- Validate and parse the AI response
- Retry once if the response is not valid JSON
- Raise structured, typed errors for:
    * Invalid / missing API key
    * Network failures
    * Gemini rate limits
    * Empty AI responses
    * Invalid JSON after retries

Reference: architecture_final.md Ãƒâ€šÃ‚Â§5.3 (Agent 2: Product Intelligence Agent)
"""
import asyncio
import json
import logging
import time
from asyncio import TimeoutError as AsyncTimeoutError
from typing import Any, Dict, Optional

from app.core.config import settings
from app.utils.metrics import metrics

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Typed error hierarchy ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â allows routers to map exceptions to HTTP status codes
# ---------------------------------------------------------------------------


class GeminiServiceError(Exception):
    """Base class for all Gemini service errors."""

    status_code = 500
    code = "gemini_error"

    def __init__(self, message: str, *, detail: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def to_dict(self) -> Dict[str, Any]:
        """Structured error payload for API responses."""
        return {
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
        }


class GeminiConfigurationError(GeminiServiceError):
    """Raised when the GEMINI_API_KEY is missing or invalid."""

    status_code = 503
    code = "gemini_configuration_error"


class GeminiNetworkError(GeminiServiceError):
    """Raised when the Gemini API cannot be reached (network failure)."""

    status_code = 503
    code = "gemini_network_error"


class GeminiRequestError(GeminiServiceError):
    # Raised for non-transient provider request errors.

    status_code = 400
    code = "gemini_request_error"

class GeminiRateLimitError(GeminiServiceError):
    """Raised when the Gemini API rate limit / quota is exceeded."""

    status_code = 429
    code = "gemini_rate_limit_exceeded"


class GeminiEmptyResponseError(GeminiServiceError):
    """Raised when Gemini returns an empty or blank response."""

    status_code = 502
    code = "gemini_empty_response"


class GeminiInvalidResponseError(GeminiServiceError):
    """Raised when Gemini returns invalid JSON after the retry."""

    status_code = 502
    code = "gemini_invalid_response"


# ---------------------------------------------------------------------------
# Required output schema ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â the ONLY structure Gemini is allowed to return
# ---------------------------------------------------------------------------
REQUIRED_FIELDS: Dict[str, type] = {
    "title": str,
    "category": str,
    "description": str,
    "key_features": list,
    "technical_specifications": dict,
    "applications": list,
    "seo_keywords": list,
    "confidence_reason": str,
}

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = (
    "You are an expert product intelligence engineer for industrial and "
    "electronic commerce. You transform minimal manufacturer data into rich, "
    "structured, commerce-ready product intelligence."
)

OUTPUT_FORMAT_INSTRUCTION = (
    "Respond with ONLY a single valid JSON object. Do NOT wrap it in markdown "
    "code fences, do NOT include any prose, commentary, or explanation before "
    "or after the JSON. The JSON MUST exactly match this schema:\n"
    "{\n"
    '  "title": "",\n'
    '  "category": "",\n'
    '  "description": "",\n'
    '  "key_features": [],\n'
    '  "technical_specifications": {},\n'
    '  "applications": [],\n'
    '  "seo_keywords": [],\n'
    '  "confidence_reason": ""\n'
    "}\n"
    "Field requirements:\n"
    '- "title": short, professional commerce title containing the MPN.\n'
    '- "category": hierarchical category, e.g. "Semiconductors > Logic ICs > NAND Gates".\n'
    '- "description": detailed, SEO-optimized 2-3 paragraph description.\n'
    '- "key_features": array of 4-8 concise feature bullets (strings).\n'
    '- "technical_specifications": object mapping spec name to value (strings/numbers).\n'
    '- "applications": array of 3-6 real-world use cases (strings).\n'
    '- "seo_keywords": array of 5-10 search keywords (strings), MPN first.\n'
    '- "confidence_reason": one sentence explaining the confidence of this generation.\n'
)


class GeminiService:
    """
    Service for generating product intelligence via the Google Gemini API.

    Uses the official `google-genai` SDK. The SDK call is blocking, so it is
    executed in a worker thread via `asyncio.to_thread` to keep the FastAPI
    event loop responsive.
    """

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.model = model or settings.gemini_model or "gemini-2.5-flash"
        self.api_key = api_key if api_key is not None else settings.gemini_api_key
        self._client = None
        self._max_attempts = 3
        self._request_timeout_seconds = 30.0
        self._backoff_seconds = 1.0
        self.last_request_attempts = 0
        self.last_generated_data: Optional[Dict[str, Any]] = None
        self.last_failure_statuses: list[int] = []

    # -- Public API ---------------------------------------------------------

    async def generate_product_intelligence(
        self,
        mpn: str,
        brand: str,
        description: str,
    ) -> Dict[str, Any]:
        """
        Generate structured product intelligence for the given product.

        Args:
            mpn: Manufacturer Part Number.
            brand: Brand name.
            description: Short product description.

        Returns:
            Dict with keys: title, category, description, key_features,
            technical_specifications, applications, seo_keywords,
            confidence_reason.

        Raises:
            GeminiConfigurationError: Missing/invalid API key.
            GeminiNetworkError: Network failure contacting Gemini.
            GeminiRateLimitError: Gemini rate limit / quota exceeded.
            GeminiEmptyResponseError: Empty AI response.
            GeminiInvalidResponseError: Invalid JSON after retries.
        """
        # Fail fast on a missing API key so callers get a clear 503.
        if not self.api_key:
            raise GeminiConfigurationError(
                "Gemini API key is not configured. Set GEMINI_API_KEY in the .env file.",
                detail="GEMINI_API_KEY is empty or missing.",
            )

        prompt = self._build_prompt(mpn=mpn, brand=brand, description=description)
        logger.info(
            "Invoking Gemini for product intelligence: mpn=%s brand=%s model=%s",
            mpn,
            brand,
            self.model,
        )

        last_error: Optional[Exception] = None
        attempts = self._max_attempts
        self.last_request_attempts = 0
        self.last_generated_data = None
        self.last_failure_statuses = []
        for attempt in range(1, attempts + 1):
            self.last_request_attempts = attempt
            try:
                raw_text = await self._invoke_gemini(prompt)
                data = self._parse_and_validate(raw_text)
                metrics.track_gemini_call(self.model, tokens=0)
                self.last_generated_data = data
                logger.info("gemini_event=success mpn=%s attempt=%d/%d", mpn, attempt, attempts)
                return data
            except GeminiInvalidResponseError as exc:
                last_error = exc
                failure_type = "invalid_response"
            except GeminiNetworkError as exc:
                last_error = exc
                failure_type = "transient_network"
                self.last_failure_statuses.append(exc.status_code)
            except GeminiServiceError:
                logger.error("gemini_event=final_failure mpn=%s attempt=%d failure_type=permanent", mpn, attempt)
                raise
            retryable = isinstance(last_error, (GeminiInvalidResponseError, GeminiNetworkError))
            if not retryable or attempt >= attempts:
                logger.error("gemini_event=final_failure mpn=%s attempt=%d failure_type=%s", mpn, attempt, failure_type)
                break
            delay = self._backoff_seconds * (2 ** (attempt - 1))
            logger.warning("gemini_event=retry mpn=%s attempt=%d/%d failure_type=%s http_status=%s retry_delay_seconds=%.1f", mpn, attempt, attempts, failure_type, getattr(last_error, "status_code", "none"), delay)
            await asyncio.sleep(delay)

        if isinstance(last_error, GeminiInvalidResponseError):
            raise GeminiInvalidResponseError("Gemini returned invalid JSON after retries.", detail="Invalid AI response after bounded retries.") from last_error
        raise GeminiNetworkError("Gemini API remained unavailable after bounded retries.", detail="Transient failure after bounded retries.") from last_error

    # -- Internal helpers ---------------------------------------------------

    def _get_client(self):
        """
        Lazily build the Google GenAI client.

        Returns:
            The `google.genai.Client` instance.

        Raises:
            GeminiConfigurationError: If the SDK is unavailable or API key is invalid.
        """
        if self._client is not None:
            return self._client

        try:
            from google import genai  # Official Google Generative AI SDK.
        except ImportError as exc:  # pragma: no cover - defensive.
            raise GeminiConfigurationError(
                "The Google Generative AI SDK is not installed. "
                "Run: pip install google-genai",
                detail=str(exc),
            ) from exc

        try:
            self._client = genai.Client(api_key=self.api_key)
        except Exception as exc:  # pragma: no cover - defensive.
            raise GeminiConfigurationError(
                "Failed to initialize the Gemini client.",
                detail=str(exc),
            ) from exc

        return self._client

    async def _invoke_gemini(self, prompt: str) -> str:
        """
        Execute a single (blocking) Gemini generation call in a worker thread.

        Args:
            prompt: The fully-formatted prompt.

        Returns:
            The raw text response from Gemini.

        Raises:
            GeminiConfigurationError: Invalid API key (401/403).
            GeminiRateLimitError: Rate limit / quota exceeded (429).
            GeminiNetworkError: Network or API failures.
            GeminiEmptyResponseError: Empty response text.
        """
        try:
            raw_text = await asyncio.wait_for(asyncio.to_thread(self._invoke_gemini_sync, prompt), timeout=self._request_timeout_seconds)
        except AsyncTimeoutError as exc:
            raise GeminiNetworkError("Gemini request timed out.", detail="Request exceeded the configured timeout.") from exc
        except GeminiServiceError:
            raise
        except Exception as exc:
            raise GeminiNetworkError(
                "Unexpected error while calling Gemini.",
                detail=str(exc),
            ) from exc

        if not raw_text or not raw_text.strip():
            raise GeminiEmptyResponseError(
                "Gemini returned an empty response.",
                detail="No content was returned by the model.",
            )

        return raw_text

    def _invoke_gemini_sync(self, prompt: str) -> str:
        """
        Synchronous Gemini call (runs inside a worker thread).

        Args:
            prompt: The fully-formatted prompt.

        Returns:
            The raw response text.

        Raises:
            GeminiConfigurationError: Invalid API key.
            GeminiRateLimitError: Rate limit / quota exceeded.
            GeminiNetworkError: Network / API failures.
        """
        client = self._get_client()
        started = time.perf_counter()

        try:
                response = self._generate_content(client, prompt)
        except Exception as exc:
                raise self._normalize_provider_error(exc) from exc
        finally:
                elapsed_ms = int((time.perf_counter() - started) * 1000)
                logger.debug("Gemini call completed in %dms", elapsed_ms)

        return self._extract_response_text(response)

        def _generate_content(self, client, prompt: str):
            from google.genai import types as genai_types
            return client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0.4,
                ),
            )

        @staticmethod
        def _normalize_provider_error(exc: Exception) -> GeminiServiceError:
            status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            message = str(exc).lower()
            if status == 429 or "429" in message or "quota" in message or "resource exhausted" in message:
                return GeminiRateLimitError("Gemini API rate limit exceeded. Please try again later.", detail=str(exc))
            if status in (401, 403) or "api key" in message or "apikey" in message or "permission" in message:
                return GeminiConfigurationError("Invalid or unauthorized Gemini API key.", detail=str(exc))
            if isinstance(status, int) and status in (500, 502, 503, 504):
                error = GeminiNetworkError("Gemini API is temporarily unavailable. Please retry shortly.", detail="Transient provider failure.")
                error.status_code = status
                return error
            if isinstance(status, int) and 400 <= status < 500:
                error = GeminiRequestError("Gemini rejected the request.", detail="Non-transient provider request error.")
                error.status_code = status
                return error
            return GeminiNetworkError("Failed to reach the Gemini API.", detail="Transient network failure.")

        @staticmethod
        def _extract_response_text(response) -> str:
            text = getattr(response, "text", None)
            if text:
                return text
            try:
                candidates = getattr(response, "candidates", None) or []
                parts = getattr(getattr(candidates[0], "content", None), "parts", None) or []
                return getattr(parts[0], "text", None) or "" if parts and candidates else ""
            except (IndexError, AttributeError, TypeError):
                return ""

    def _build_prompt(self, mpn: str, brand: str, description: str) -> str:
        """
        Build the strict JSON-only prompt for Gemini.

        Args:
            mpn: Manufacturer Part Number.
            brand: Brand name.
            description: Short product description.

        Returns:
            Formatted prompt string.
        """
        return (
            f"{SYSTEM_INSTRUCTION}\n\n"
            f"{OUTPUT_FORMAT_INSTRUCTION}\n\n"
            "Product information:\n"
            f"- Manufacturer Part Number (MPN): {mpn}\n"
            f"- Brand: {brand}\n"
            f"- Short Description: {description}\n\n"
            "Now generate the product intelligence JSON."
        )

    def _parse_and_validate(self, raw_text: str) -> Dict[str, Any]:
        """
        Extract and validate JSON from the model response.

        Attempts to parse the raw text as JSON. If that fails, it tries to
        extract the first JSON object embedded in the text (e.g., wrapped in
        code fences) as a fallback.

        Args:
            raw_text: The raw Gemini response text.

        Returns:
            The validated JSON payload as a dict.

        Raises:
            GeminiInvalidResponseError: If JSON cannot be parsed or the
            required fields are missing.
        """
        data: Optional[Dict[str, Any]] = None

        # Attempt 1: direct JSON parse.
        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                data = parsed
        except (json.JSONDecodeError, TypeError):
            data = None

        # Attempt 2: extract JSON embedded in markdown/code fences.
        if data is None:
            data = self._extract_json(raw_text)

        if data is None:
            raise GeminiInvalidResponseError(
                "Gemini response could not be parsed as JSON.",
                detail=raw_text[:500],
            )

        # Validate required fields and nested collection members.
        invalid = [
            field for field, expected_type in REQUIRED_FIELDS.items()
            if field not in data or not isinstance(data.get(field), expected_type)
        ]
        for field in ("key_features", "applications", "seo_keywords"):
            if field in data and isinstance(data[field], list):
                invalid.extend(f"{field}[{index}]" for index, value in enumerate(data[field]) if not isinstance(value, str))
        if "technical_specifications" in data and isinstance(data["technical_specifications"], dict):
            invalid.extend(
                f"technical_specifications[{key}]"
                for key, value in data["technical_specifications"].items()
                if not isinstance(key, str) or not isinstance(value, (str, int, float, bool))
            )
        if invalid:
            raise GeminiInvalidResponseError(
                "Gemini response contains missing or invalid fields.",
                detail=f"Missing/invalid fields: {', '.join(invalid)}",
            )

        return data

    @staticmethod
    def _extract_json(raw_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract the first JSON object from text that may contain markdown.

        Handles code fences and leading/trailing prose by scanning for the
        first '{' and matching the final '}' via a bracket-depth scan.

        Args:
            raw_text: The raw Gemini response text.

        Returns:
            Parsed dict if a JSON object was found, None otherwise.
        """
        start = raw_text.find("{")
        if start == -1:
            return None

        depth = 0
        in_string = False
        escape = False
        for idx in range(start, len(raw_text)):
            ch = raw_text[idx]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = raw_text[start : idx + 1]
                    try:
                        parsed = json.loads(candidate)
                        return parsed if isinstance(parsed, dict) else None
                    except json.JSONDecodeError:
                        return None
        return None



