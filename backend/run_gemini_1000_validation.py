"Resumable, paced Gemini validation for the 1,000-row workbook."""
from __future__ import annotations
import asyncio
import csv
import json
import time
from pathlib import Path
from typing import Any, Dict, List
from app.schemas.request import ProductRequest
from app.services.dataset_evaluation_service import clean, column, is_placeholder, load_rows, normalize_name, normalize_mpn, select_brand
from app.services.gemini_service import GeminiService, GeminiServiceError
from app.services.product_service import ProductService
DATASET = Path(r"C:\Users\megha\OneDrive\Desktop\Unihack- Sample Dataset.xlsx")
REPORT_DIR = Path(__file__).resolve().parent / "evaluation_reports"
CHECKPOINT = REPORT_DIR / "gemini_1000_checkpoint.json"
FINAL_JSON = REPORT_DIR / "gemini_1000_products.json"
FINAL_CSV = REPORT_DIR / "gemini_1000_rows.csv"
SUMMARY_JSON = REPORT_DIR / "gemini_1000_summary.json"
FAILED_JSON = REPORT_DIR / "gemini_1000_failed_rows.json"
REQUIRED_FIELDS = ("title", "category", "description", "key_features", "technical_specifications", "applications", "seo_keywords", "confidence_reason")

def request_for_row(row: Dict[str, Any]) -> ProductRequest:
    mpn = normalize_mpn(column(row, "Mfg_Part_Num", "MPN", "PART_NUMBER")) or "UNKNOWN-MPN"
    brand, _ = select_brand(row)
    manufacturer = normalize_name(column(row, "Part_Manuf", "Manufacturer"))
    prompt_brand = brand or (f"Unbranded product ({manufacturer})" if manufacturer else "Unbranded product")
    description = clean(column(row, "Part_Desc", "Description")) or "Product details unavailable."
    return ProductRequest(mpn=mpn, brand=prompt_brand, description=description[:1000])


def validate(data: Dict[str, Any]) -> Dict[str, Any]:
    expected = {"title": str, "category": str, "description": str, "key_features": list, "technical_specifications": dict, "applications": list, "seo_keywords": list, "confidence_reason": str}
    missing = [field for field in REQUIRED_FIELDS if field not in data or data[field] in (None, "", [], {})]
    invalid = [field for field, kind in expected.items() if field in data and not isinstance(data[field], kind)]
    return {"valid": not missing and not invalid, "missing_fields": missing, "invalid_fields": invalid}


def load_checkpoint() -> Dict[str, Dict[str, Any]]:
    if not CHECKPOINT.exists():
        return {}
    try:
        return {str(item["row_number"]): item for item in json.loads(CHECKPOINT.read_text(encoding="utf-8"))}
    except (OSError, ValueError, KeyError, TypeError):
        return {}


def save_checkpoint(results: Dict[str, Dict[str, Any]]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(json.dumps(list(results.values()), ensure_ascii=False), encoding="utf-8")


def write_csv(results: List[Dict[str, Any]]) -> None:
    with FINAL_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = ("row_number", "mpn", "status", "latency_ms", "attempt_count", "retry_count", "transient_errors", "final_error", "validation_valid", "missing_fields", "invalid_fields", "provenance")
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in results:
            error = item.get("error", {})
            validation = item.get("validation", {})
            writer.writerow({"row_number": item["row_number"], "mpn": item["mpn"], "status": item["status"], "latency_ms": item.get("latency_ms", ""), "attempt_count": item.get("attempt_count", 0), "retry_count": item.get("retry_count", 0), "transient_errors": ";".join(str(x) for x in item.get("failure_statuses", [])), "final_error": error.get("code", ""), "validation_valid": validation.get("valid", False), "missing_fields": ";".join(validation.get("missing_fields", [])), "invalid_fields": ";".join(validation.get("invalid_fields", [])), "provenance": json.dumps(item.get("provenance", {}), ensure_ascii=False)})

async def run() -> Dict[str, Any]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows(DATASET)
    results = load_checkpoint()
    started = time.perf_counter()
    stop_for_rate_limit = False
    run_started_at = time.time()
    for row_number, row in enumerate(rows, 2):
        key = str(row_number)
        if key in results and results[key].get("status") == "success":
            continue
        request = request_for_row(row)
        gemini = GeminiService()
        service = ProductService(gemini_service=gemini)
        request_started = time.perf_counter()
        item = {"row_number": row_number, "mpn": request.mpn, "input": dict(row), "request": request.model_dump(), "status": "failed"}
        try:
            product = await service.analyze(request)
            validation = validate(gemini.last_generated_data or {})
            item.update({"status": "success", "generated_output": product.model_dump(), "provenance": {"sources": [source.model_dump() for source in product.sources], "agent_timeline": [entry.model_dump() for entry in product.agent_timeline]}, "validation": validation})
        except GeminiServiceError as exc:
            item.update({"error": {"code": exc.code, "status_code": exc.status_code, "message": exc.message}, "provenance": {}, "validation": {"valid": False, "missing_fields": [], "invalid_fields": []}, "rate_limit": exc.status_code == 429, "api_error": True})
            if exc.status_code == 429:
                stop_for_rate_limit = True
        except Exception as exc:
            item.update({"error": {"code": "unexpected_error", "message": str(exc)}, "provenance": {}, "validation": {"valid": False, "missing_fields": [], "invalid_fields": []}, "rate_limit": False, "api_error": False})
        item.update({"latency_ms": round((time.perf_counter() - request_started) * 1000, 2), "attempt_count": gemini.last_request_attempts, "retry_count": max(gemini.last_request_attempts - 1, 0), "failure_statuses": gemini.last_failure_statuses})
        results[key] = item
        save_checkpoint(results)
        write_csv(sorted(results.values(), key=lambda value: value["row_number"]))
        if len(results) % 10 == 0:
            (REPORT_DIR / "gemini_1000_progress.json").write_text(json.dumps({"products_tested": len(results), "successful_products": sum(value.get("status") == "success" for value in results.values()), "failed_products": sum(value.get("status") != "success" for value in results.values()), "elapsed_seconds": round(time.time() - run_started_at, 2)}, indent=2), encoding="utf-8")
        if stop_for_rate_limit:
            break
        await asyncio.sleep(0.02)
    ordered = sorted(results.values(), key=lambda value: value["row_number"])
    successful = [item for item in ordered if item["status"] == "success"]
    failed = [item for item in ordered if item["status"] != "success"]
    latencies = [item["latency_ms"] for item in ordered if "latency_ms" in item]
    status_counts: Dict[str, int] = {}
    for item in ordered:
        for status in item.get("failure_statuses", []):
            status_counts[str(status)] = status_counts.get(str(status), 0) + 1
    missing = sum(len(item.get("validation", {}).get("missing_fields", [])) for item in ordered)
    summary = {"total_products": len(rows), "products_tested": len(ordered), "successful_products": len(successful), "failed_products": len(failed), "success_percentage": round(len(successful) / len(rows) * 100, 2) if rows else 0, "total_processing_time_seconds": round(time.perf_counter() - started, 2), "average_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0, "minimum_latency_ms": min(latencies) if latencies else 0, "maximum_latency_ms": max(latencies) if latencies else 0, "retry_count": sum(item.get("retry_count", 0) for item in ordered), "http_5xx_occurrences": sum(count for status, count in status_counts.items() if status in {"500", "502", "503", "504"}), "503_occurrences": status_counts.get("503", 0), "timeout_occurrences": sum(1 for item in ordered if item.get("error", {}).get("code") == "gemini_network_error" and "timed out" in item.get("error", {}).get("message", "").lower()), "rate_limit_occurrences": sum(1 for item in ordered if item.get("rate_limit")), "other_api_errors": sum(1 for item in ordered if item.get("api_error") and not item.get("rate_limit")), "validation_failures": sum(1 for item in ordered if not item.get("validation", {}).get("valid", False)), "missing_fields": missing, "generated_field_completeness": round(sum(1 for item in successful if item.get("validation", {}).get("valid")) / len(successful) * 100, 2) if successful else 0, "ground_truth_available": False, "accuracy_claimed": False, "rate_limit_stop": stop_for_rate_limit, "supports_all_252_delivery_fields": False, "resumable": len(ordered) < len(rows) or not stop_for_rate_limit}
    FINAL_JSON.write_text(json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8")
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    FAILED_JSON.write_text(json.dumps(failed, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary
if __name__ == "__main__":
    print(json.dumps(asyncio.run(run()), indent=2))
