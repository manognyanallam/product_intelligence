"Run a controlled Gemini enrichment smoke test on representative workbook rows."""
from __future__ import annotations
import asyncio
import csv
import json
import time
from pathlib import Path
from typing import Any, Dict, List
from app.schemas.request import ProductRequest
from app.services.dataset_evaluation_service import (
    clean,
    column,
    is_placeholder,
    load_rows,
    normalize_name,
    normalize_mpn,
    select_brand,
)
from app.services.gemini_service import GeminiService, GeminiServiceError
from app.services.product_service import ProductService
DATASET = Path(r"C:\Users\megha\OneDrive\Desktop\Unihack- Sample Dataset.xlsx")
REPORT_DIR = Path(__file__).resolve().parent / "evaluation_reports"
REQUIRED_GENERATED_FIELDS = (
    "title", "category", "description", "key_features",
    "technical_specifications", "applications", "seo_keywords",
    "confidence_reason",
)


def select_representative_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Select eight rows with unique normalized MPNs and varied conditions.
    selected: List[Dict[str, Any]] = []
    seen_mpns = set()
    candidates = []
    for row in rows:
        mpn = normalize_mpn(column(row, "Mfg_Part_Num", "MPN", "PART_NUMBER"))
        if mpn and mpn not in seen_mpns:
            candidates.append((mpn, row))
            seen_mpns.add(mpn)
    selected = [row for _, row in candidates[:4]]
    used = {normalize_mpn(column(row, "Mfg_Part_Num", "MPN", "PART_NUMBER")) for row in selected}
    for keyword in ("belt", "saw", "valve", "connector", "switch"):
        for mpn, row in candidates:
            desc = clean(column(row, "Part_Desc", "Description")).lower()
            if mpn not in used and keyword in desc:
                selected.append(row)
                used.add(mpn)
                break
        if len(selected) >= 8:
            break
    for mpn, row in candidates:
        if len(selected) >= 8:
            break
        if mpn not in used:
            selected.append(row)
            used.add(mpn)
    return selected[:8]


def input_for_row(row: Dict[str, Any]) -> ProductRequest:
    mpn = normalize_mpn(column(row, "Mfg_Part_Num", "MPN", "PART_NUMBER")) or "UNKNOWN-MPN"
    brand, _ = select_brand(row)
    manufacturer = normalize_name(column(row, "Part_Manuf", "Manufacturer"))
    # ProductRequest requires a non-empty brand; preserve placeholder semantics explicitly.
    prompt_brand = brand or (f"Unbranded product ({manufacturer})" if manufacturer else "Unbranded product")
    description = clean(column(row, "Part_Desc", "Description")) or "Product details unavailable."
    return ProductRequest(mpn=mpn, brand=prompt_brand, description=description[:1000])


def validate_generated(data: Dict[str, Any]) -> Dict[str, Any]:
    missing = [field for field in REQUIRED_GENERATED_FIELDS if field not in data or data[field] in (None, "", [], {})]
    invalid_types = []
    expected = {"title": str, "category": str, "description": str, "key_features": list, "technical_specifications": dict, "applications": list, "seo_keywords": list, "confidence_reason": str}
    for field, field_type in expected.items():
        if field in data and not isinstance(data[field], field_type):
            invalid_types.append(field)
    return {"missing_fields": missing, "invalid_fields": invalid_types, "valid": not missing and not invalid_types}

async def run() -> Dict[str, Any]:
    rows = load_rows(DATASET)
    selected = select_representative_rows(rows)
    results: List[Dict[str, Any]] = []
    for position, row in enumerate(selected, 1):
        request = input_for_row(row)
        gemini = GeminiService()
        service = ProductService(gemini_service=gemini)
        started = time.perf_counter()
        result: Dict[str, Any] = {"test_index": position, "dataset_row": row, "request": request.model_dump(), "status": "failed"}
        try:
            product = await service.analyze(request)
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            generated = product.enriched_data.model_dump()
            raw_generated = gemini.last_generated_data or {}
            validation = validate_generated(raw_generated)
            result.update({"status": "success", "latency_ms": latency_ms, "retry_count": max(gemini.last_request_attempts - 1, 0), "failure_statuses": gemini.last_failure_statuses, "generated_output": product.model_dump(), "provenance": {"sources": [source.model_dump() for source in product.sources], "agent_timeline": [item.model_dump() for item in product.agent_timeline]}, "validation": validation, "rate_limit": False, "api_error": False})
        except GeminiServiceError as exc:
            result.update({"latency_ms": round((time.perf_counter() - started) * 1000, 2), "retry_count": max(gemini.last_request_attempts - 1, 0), "failure_statuses": gemini.last_failure_statuses, "error": {"code": exc.code, "status_code": exc.status_code, "message": exc.message}, "rate_limit": exc.status_code == 429, "api_error": True, "validation": {"valid": False, "missing_fields": [], "invalid_fields": []}})
        except Exception as exc:
            result.update({"latency_ms": round((time.perf_counter() - started) * 1000, 2), "retry_count": max(gemini.last_request_attempts - 1, 0), "error": {"code": "unexpected_error", "message": str(exc)}, "rate_limit": False, "api_error": False, "validation": {"valid": False, "missing_fields": [], "invalid_fields": []}})
        results.append(result)
    successful = [item for item in results if item["status"] == "success"]
    latencies = [item["latency_ms"] for item in results]
    missing = sum(len(item.get("validation", {}).get("missing_fields", [])) for item in results)
    status_counts = {}
    for item in results:
        for status in item.get("failure_statuses", []):
            status_counts[str(status)] = status_counts.get(str(status), 0) + 1
    summary = {"products_tested": len(results), "successful_requests": len(successful), "failed_requests": len(results) - len(successful), "average_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0, "minimum_latency_ms": min(latencies) if latencies else 0, "maximum_latency_ms": max(latencies) if latencies else 0, "retry_count": sum(item.get("retry_count", 0) for item in results), "503_occurrences": status_counts.get("503", 0), "transient_status_counts": status_counts, "rate_limit_count": sum(1 for item in results if item.get("rate_limit")), "api_error_count": sum(1 for item in results if item.get("api_error")), "validation_failures": sum(1 for item in results if not item.get("validation", {}).get("valid", False)), "missing_fields": missing, "generated_field_completeness": round(sum(1 for item in successful if item["validation"]["valid"]) / len(successful) * 100, 2) if successful else 0, "ground_truth_available": False, "accuracy_claimed": False, "demo_readiness": len(results) == 8 and len(successful) == 8 and missing == 0 and not any(item.get("api_error") for item in results)}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "gemini_batch_test.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (REPORT_DIR / "gemini_batch_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    with (REPORT_DIR / "gemini_batch_test.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("test_index", "status", "mpn", "latency_ms", "retry_count", "error_code", "error_status", "rate_limit", "validation_valid", "missing_fields", "invalid_fields"))
        writer.writeheader()
        for item in results:
            error = item.get("error", {})
            validation = item.get("validation", {})
            writer.writerow({"test_index": item["test_index"], "status": item["status"], "mpn": item["request"]["mpn"], "latency_ms": item.get("latency_ms", ""), "retry_count": item.get("retry_count", 0), "error_code": error.get("code", ""), "error_status": error.get("status_code", ""), "rate_limit": item.get("rate_limit", False), "validation_valid": validation.get("valid", False), "missing_fields": ";".join(validation.get("missing_fields", [])), "invalid_fields": ";".join(validation.get("invalid_fields", []))})
    return summary
if __name__ == "__main__":
    print(json.dumps(asyncio.run(run()), indent=2))
