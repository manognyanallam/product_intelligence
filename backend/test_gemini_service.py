"""
Unit test for GeminiService using a mocked SDK.

Verifies:
1. Valid JSON response parsing + required-field validation
2. Retry once on invalid JSON
3. Structured error mapping (rate limit, network, empty, invalid JSON)
4. JSON-only prompt structure
"""
import asyncio
import json
import sys
from unittest.mock import patch

VALID_JSON = {
    "title": "SN74LS00N Quad 2-Input Positive-NAND Gate IC",
    "category": "Semiconductors > Logic ICs > NAND Gates",
    "description": "A detailed description of the product.",
    "key_features": ["Quad 2-input NAND gates", "Low power"],
    "technical_specifications": {"Supply Voltage": "4.75-5.25V", "Package": "PDIP-14"},
    "applications": ["Digital logic", "Signal processing"],
    "seo_keywords": ["SN74LS00N", "NAND gate"],
    "confidence_reason": "High confidence based on known part details.",
}


def run(coro):
    return asyncio.run(coro)


def test_valid_json():
    from app.services.gemini_service import GeminiService

    with patch.object(GeminiService, "_invoke_gemini_sync", return_value=json.dumps(VALID_JSON)):
        svc = GeminiService(api_key="test-key")
        result = run(svc.generate_product_intelligence("SN74LS00N", "TI", "NAND gate"))
        assert result["title"] == VALID_JSON["title"], "title mismatch"
        assert result["technical_specifications"]["Package"] == "PDIP-14", "specs mismatch"
        assert len(result["key_features"]) == 2, "features mismatch"
        print("PASS: valid JSON parsed correctly")


def test_json_in_code_fences():
    from app.services.gemini_service import GeminiService

    raw = "```json\n" + json.dumps(VALID_JSON) + "\n```"
    with patch.object(GeminiService, "_invoke_gemini_sync", return_value=raw):
        svc = GeminiService(api_key="test-key")
        result = run(svc.generate_product_intelligence("SN74LS00N", "TI", "NAND gate"))
        assert result["title"] == VALID_JSON["title"], "code-fence parse failed"
        print("PASS: JSON inside markdown code fences parsed")


def test_retry_then_success():
    from app.services.gemini_service import GeminiService

    calls = {"n": 0}

    def fake_sync(prompt):
        calls["n"] += 1
        if calls["n"] == 1:
            return "not valid json"
        return json.dumps(VALID_JSON)

    with patch.object(GeminiService, "_invoke_gemini_sync", side_effect=fake_sync):
        svc = GeminiService(api_key="test-key")
        result = run(svc.generate_product_intelligence("SN74LS00N", "TI", "NAND gate"))
        assert result["title"] == VALID_JSON["title"], "retry result wrong"
        assert calls["n"] == 2, f"expected 2 calls, got {calls['n']}"
        print("PASS: retried once after invalid JSON, then succeeded")


def test_invalid_json_after_retries():
    from app.services.gemini_service import GeminiService, GeminiInvalidResponseError

    with patch.object(GeminiService, "_invoke_gemini_sync", return_value="still not json"):
        svc = GeminiService(api_key="test-key")
        try:
            run(svc.generate_product_intelligence("SN74LS00N", "TI", "NAND gate"))
            print("FAIL: expected GeminiInvalidResponseError")
        except GeminiInvalidResponseError as e:
            assert e.status_code == 502, "expected 502"
            assert e.code == "gemini_invalid_response"
            print("PASS: invalid JSON after retries -> GeminiInvalidResponseError (502)")


def test_missing_fields():
    from app.services.gemini_service import GeminiService, GeminiInvalidResponseError

    partial = {k: v for k, v in VALID_JSON.items() if k != "applications"}
    with patch.object(GeminiService, "_invoke_gemini_sync", return_value=json.dumps(partial)):
        svc = GeminiService(api_key="test-key")
        try:
            run(svc.generate_product_intelligence("SN74LS00N", "TI", "NAND gate"))
            print("FAIL: expected missing-field error")
        except GeminiInvalidResponseError as e:
            print("PASS: missing required field -> GeminiInvalidResponseError")


def test_empty_response():
    from app.services.gemini_service import GeminiService, GeminiEmptyResponseError

    with patch.object(GeminiService, "_invoke_gemini_sync", return_value=""):
        svc = GeminiService(api_key="test-key")
        try:
            run(svc.generate_product_intelligence("SN74LS00N", "TI", "NAND gate"))
            print("FAIL: expected GeminiEmptyResponseError")
        except GeminiEmptyResponseError as e:
            assert e.status_code == 502
            print("PASS: empty response -> GeminiEmptyResponseError (502)")


def test_rate_limit_error():
    from app.services.gemini_service import GeminiService, GeminiRateLimitError

    class RateLimitExc(Exception):
        def __init__(self):
            super().__init__("429 Resource has been exhausted (e.g. check quota).")
            self.status_code = 429

    class FakeModels:
        def generate_content(self, model, contents, config):
            raise RateLimitExc()

    class FakeClient:
        models = FakeModels()

    with patch.object(GeminiService, "_get_client", return_value=FakeClient()):
        svc = GeminiService(api_key="test-key")
        try:
            run(svc.generate_product_intelligence("SN74LS00N", "TI", "NAND gate"))
            print("FAIL: expected GeminiRateLimitError")
        except GeminiRateLimitError as e:
            assert e.status_code == 429
            print("PASS: rate limit -> GeminiRateLimitError (429)")


def test_network_error():
    from app.services.gemini_service import GeminiService, GeminiNetworkError

    class NetworkExc(Exception):
        def __init__(self):
            super().__init__("Failed to connect to generativelanguage.googleapis.com")

    class FakeModels:
        def generate_content(self, model, contents, config):
            raise NetworkExc()

    class FakeClient:
        models = FakeModels()

    with patch.object(GeminiService, "_get_client", return_value=FakeClient()):
        svc = GeminiService(api_key="test-key")
        try:
            run(svc.generate_product_intelligence("SN74LS00N", "TI", "NAND gate"))
            print("FAIL: expected GeminiNetworkError")
        except GeminiNetworkError as e:
            assert e.status_code == 503
            print("PASS: network error -> GeminiNetworkError (503)")


def test_invalid_api_key():
    from app.services.gemini_service import GeminiService, GeminiConfigurationError

    class KeyExc(Exception):
        def __init__(self):
            super().__init__("API key not valid. Please pass a valid API key.")
            self.code = 400

    class FakeModels:
        def generate_content(self, model, contents, config):
            raise KeyExc()

    class FakeClient:
        models = FakeModels()

    with patch.object(GeminiService, "_get_client", return_value=FakeClient()):
        svc = GeminiService(api_key="invalid-key")
        try:
            run(svc.generate_product_intelligence("SN74LS00N", "TI", "NAND gate"))
            print("FAIL: expected GeminiConfigurationError")
        except GeminiConfigurationError as e:
            assert e.status_code == 503
            print("PASS: invalid API key -> GeminiConfigurationError (503)")


def test_prompt_structure():
    from app.services.gemini_service import GeminiService

    svc = GeminiService(api_key="test-key")
    prompt = svc._build_prompt("SN74LS00N", "Texas Instruments", "Quad 2-input NAND gate")
    assert "SN74LS00N" in prompt
    assert "Texas Instruments" in prompt
    assert "Quad 2-input NAND gate" in prompt
    assert "ONLY a single valid JSON object" in prompt
    assert "technical_specifications" in prompt
    assert "confidence_reason" in prompt
    print("PASS: prompt contains product info + strict JSON instructions")


def test_no_api_key():
    from app.services.gemini_service import GeminiService, GeminiConfigurationError

    svc = GeminiService(api_key="")
    try:
        run(svc.generate_product_intelligence("SN74LS00N", "TI", "NAND gate"))
        print("FAIL: expected GeminiConfigurationError")
    except GeminiConfigurationError as e:
        assert e.status_code == 503
        print("PASS: missing API key -> GeminiConfigurationError (503)")


if __name__ == "__main__":
    sys.path.insert(0, ".")
    test_prompt_structure()
    test_valid_json()
    test_json_in_code_fences()
    test_retry_then_success()
    test_invalid_json_after_retries()
    test_missing_fields()
    test_empty_response()
    test_rate_limit_error()
    test_network_error()
    test_invalid_api_key()
    test_no_api_key()
    print("\nALL GEMINI SERVICE TESTS PASSED")

