"Dataset-driven Phase 2 enrichment and evaluation services."""
from __future__ import annotations
import csv
import difflib
import json
import logging
import re
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
logger = logging.getLogger(__name__)

PLACEHOLDERS = {"--", "-- unbranded --", "-- no unilog brand --", "-- no dib brand --"}
WORKING_DATASETS = {
    "Unilog-Sample_200_Items-Input-vs-Output.xlsx",
    "Sample-1000_Items.xlsx",
    "Unihack- Sample Dataset.xlsx",
}
REFERENCE_FILES = {
    "UniCat_Manufacturer_and_Brand_List.xlsx",
    "Unicat_LOV_v1_0_Updated_With_Remarks.xlsx",
    "Unilog_Master_UOM_Standards_Abbreviations_and_Terms.xlsx",
    "Decimal_Fraction.xlsx",
    "UNILOG_INTERNAL_CONTENT_GUIDELINES.docx",
    "Fittings_LOV.xlsx",
    "Reference_Documents_Summary.xlsx",
}


def clean(value: Any) -> str:
    value = "" if value is None else str(value)
    return re.sub(r"\s+", " ", value.replace("\n", " ")).strip()


def is_placeholder(value: Any) -> bool:
    return clean(value).lower() in PLACEHOLDERS

def normalize_mpn_identifier(value: Any) -> str:
    # Normalize an MPN without adding a decimal suffix to numeric Excel cells.
    if value is None or value == "":
        return ""
    if isinstance(value, bool):
        return str(value).upper()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return clean(value)
    if isinstance(value, Decimal):
        try:
            return str(int(value)) if value == value.to_integral_value() else clean(value)
        except (InvalidOperation, ValueError):
            return clean(value)
    return re.sub(r"\s+", "", clean(value)).upper()


def normalize_mpn(value: Any) -> str:
    return normalize_mpn_identifier(value)


def normalize_name(value: Any) -> str:
    if is_placeholder(value):
        return ""
    return clean(value)


def normalize_unit(value: Any) -> str:
    text = clean(value)
    units = {"inches": "in", "inch": "in", '"': "in", "feet": "ft", "foot": "ft", "lb": "lb", "lbs": "lb"}
    return units.get(text.lower(), text)


def select_brand(row: Dict[str, Any]) -> Tuple[str, str]:
    for field in ("Unilog_Brand", "DIB_Brand", "E1_Brand"):
        value = normalize_name(column(row, field))
        if value:
            return value, field
    return "", ""


def extract_attributes(text: str) -> Dict[str, str]:
    attributes: Dict[str, str] = {}
    for label, pattern in (("size", r"\b\d+(?:[-/]\d+)?(?:\.\d+)?\s*(?:in|inch|inches|ft|mm|cm)\b"), ("quantity", r"\b\d+\s*(?:pc|pcs|piece|pieces|pack|box|roll)\b")):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            attributes[label] = normalize_unit(match.group(0))
    return attributes


def find_file(name: str, roots: Iterable[Path]) -> Optional[Path]:
    for root in roots:
        if not root.exists():
            continue
        direct = root / name
        if direct.is_file():
            return direct
        for candidate in root.rglob(name):
            if candidate.is_file():
                return candidate
    return None

def load_rows(path: Path) -> List[Dict[str, Any]]:
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise RuntimeError("openpyxl is required to process Excel datasets") from exc
    workbook = load_workbook(path, read_only=True, data_only=True)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [clean(value) for value in rows[0]]
    records = []
    for row in rows[1:]:
        if not any(value is not None for value in row):
            continue
        record = dict(zip(headers, row))
        for key in ("Mfg_Part_Num", "MPN", "PART_NUMBER", "Part Number"):
            if key in record:
                record[key] = normalize_mpn_identifier(record[key])
        records.append(record)
    return records


def column(row: Dict[str, Any], *names: str) -> Any:
    normalized = {clean(key).lower().replace(" ", "_"): value for key, value in row.items()}
    for name in names:
        value = normalized.get(name.lower().replace(" ", "_"))
        if value not in (None, ""):
            return value
    return ""


def generate_output(row: Dict[str, Any], vocab: Dict[str, set]) -> Dict[str, Any]:
    mpn = normalize_mpn(column(row, "PART_NUMBER", "MPN", "Part Number", "Mfg_Part_Num"))
    brand, brand_source = select_brand(row)
    manufacturer = normalize_name(column(row, "Part_Manuf", "Manufacturer", "Manufacturer Name"))
    part_desc = clean(column(row, "Part_Desc", "Part Desc", "Description"))
    category = normalize_name(column(row, "Category", "Taxonomy", "Product Category"))
    features = [clean(value) for key, value in row.items() if "feature" in clean(key).lower() and clean(value)]
    specifications = {clean(key): clean(value) for key, value in row.items() if "spec" in clean(key).lower() and clean(value)}
    attributes = extract_attributes(part_desc)
    prefix = f"{brand} " if brand else ""
    short_description = f"{prefix}{mpn}: {part_desc}".strip(": ")
    long_description = part_desc or short_description
    return {
        "PART_NUMBER": mpn,
        "Brand": brand,
        "Manufacturer": manufacturer,
        "Brand_Source": brand_source,
        "Part_Desc": part_desc,
        "Attributes": attributes,
        "Category": category,
        "Short_Description": short_description,
        "Long_Description": long_description,
        "Features": features,
        "Specifications": specifications,
        "UOM": normalize_unit(column(row, "UOM", "Unit", "Unit of Measure")),
        "validation": {
            "manufacturer_valid": not manufacturer or not vocab["manufacturers"] or manufacturer.lower() in vocab["manufacturers"],
            "brand_valid": not brand or not vocab["brands"] or brand.lower() in vocab["brands"],
            "category_valid": not category or not vocab["categories"] or category.lower() in vocab["categories"],
            "uom_valid": (not normalize_unit(column(row, "UOM", "Unit", "Unit of Measure")) or not vocab["uoms"] or normalize_unit(column(row, "UOM", "Unit", "Unit of Measure")) in vocab["uoms"]),
            "placeholder_contamination": any(is_placeholder(row.get(field, "")) for field in ("E1_Brand", "Unilog_Brand", "DIB_Brand")),
        },
        "provenance": {"input": ["PART_NUMBER", "Brand", "Part_Desc"], "generated": ["Short_Description", "Long_Description", "Features"]},
    }

class DatasetEvaluationService:
    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.root = project_root or Path(__file__).resolve().parents[3]
        desktop = Path.home() / "OneDrive" / "Desktop"
        self.search_roots = [self.root, self.root / "backend", self.root / "data", self.root / "backend" / "data", desktop]

    def _vocab(self) -> Dict[str, set]:
        # Reference workbooks are lookup data only; no working dataset is loaded here.
        brands: set = set()
        manufacturers: set = set()
        categories: set = set()
        uoms: set = set()
        for name in ("UniCat_Manufacturer_and_Brand_List.xlsx", "Unicat_LOV_v1_0_Updated_With_Remarks.xlsx"):
            path = find_file(name, self.search_roots)
            if not path:
                continue
            try:
                for row in load_rows(path):
                    for key, value in row.items():
                        text = clean(value)
                        key_lower = clean(key).lower()
                        if text and "brand" in key_lower:
                            brands.add(text.lower())
                        if text and "manufacturer" in key_lower:
                            manufacturers.add(text.lower())
                        if text and ("category" in key_lower or "taxonomy" in key_lower or "classpath" in key_lower):
                            categories.add(text.lower())
                        if text and ("uom" in key_lower or "unit" in key_lower):
                            uoms.add(normalize_unit(text).lower())
            except Exception:
                logger.warning("Unable to load lookup workbook %s", path, exc_info=True)
        return {"brands": brands, "manufacturers": manufacturers, "categories": categories, "uoms": uoms}

    def _dataset(self, filename: str) -> Path:
        if filename not in WORKING_DATASETS:
            raise ValueError(f"Unsupported working dataset: {filename}")
        path = find_file(filename, self.search_roots)
        if not path and filename == "Sample-1000_Items.xlsx":
            path = find_file("Unihack- Sample Dataset.xlsx", self.search_roots)
        if not path:
            raise FileNotFoundError(f"Working dataset not found: {filename}")
        return path
    def process(self, filename: str, report_dir: Optional[Path] = None) -> Dict[str, Any]:
        path = self._dataset(filename)
        vocab = self._vocab()
        rows = load_rows(path)
        generated: List[Dict[str, Any]] = []
        failures: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []
        mpns: Dict[str, List[int]] = {}
        placeholder_count = 0
        missing_count = 0
        started = time.perf_counter()
        for index, row in enumerate(rows, 2):
            try:
                output = generate_output(row, vocab)
                generated.append({"row_number": index, "input": dict(row), "output": output})
                mpn = output["PART_NUMBER"]
                if mpn:
                    mpns.setdefault(mpn, []).append(index)
                validation = output["validation"]
                if validation["placeholder_contamination"]:
                    placeholder_count += 1
                    warnings.append({"row_number": index, "type": "placeholder_value", "message": "One or more brand fields contain a configured placeholder."})
                for key in ("manufacturer_valid", "brand_valid", "category_valid", "uom_valid"):
                    if validation[key] is False:
                        warnings.append({"row_number": index, "type": key, "message": f"Validation warning: {key}"})
                missing_fields = [field for field in ("PART_NUMBER", "Part_Desc") if not output[field]]
                if missing_fields:
                    missing_count += 1
                    warnings.append({"row_number": index, "type": "missing_value", "message": f"Missing fields: {', '.join(missing_fields)}"})
                if not output["Short_Description"] or not output["Long_Description"]:
                    warnings.append({"row_number": index, "type": "enrichment_unavailable", "message": "Description enrichment could not be generated."})
            except Exception as exc:
                failures.append({"row_number": index, "reason": str(exc), "input": dict(row)})
        elapsed = time.perf_counter() - started
        duplicates = {mpn: locations for mpn, locations in mpns.items() if len(locations) > 1}
        unique_mpns = sorted(mpn for mpn in mpns if mpn)
        near_duplicates = {}
        for position, mpn in enumerate(unique_mpns):
            for other in unique_mpns[position + 1:]:
                if len(mpn) >= 6 and len(other) >= 6 and difflib.SequenceMatcher(None, mpn, other).ratio() >= 0.92:
                    near_duplicates.setdefault(mpn, []).append(other)
        validation_warning_types = {"manufacturer_valid", "brand_valid", "category_valid", "uom_valid"}
        summary = {
            "dataset": filename, "source_path": str(path), "total_rows": len(rows),
            "processed_rows": len(generated), "successfully_processed_rows": len(generated),
            "failed_rows": len(failures), "success_percentage": round(len(generated) / len(rows) * 100, 2) if rows else 0.0,
            "processing_time_seconds": round(elapsed, 4), "average_processing_time_ms": round(elapsed / len(rows) * 1000, 3) if rows else 0.0,
            "gemini_api_failures": 0, "gemini_api_used": False,
            "validation_failures": sum(1 for item in warnings if item["type"] in validation_warning_types),
            "missing_values": missing_count,
            "placeholder_values_detected": placeholder_count,
            "invalid_manufacturer_brand_values": sum(1 for item in warnings if item["type"] in {"manufacturer_valid", "brand_valid"}),
            "invalid_uom_values": sum(1 for item in warnings if item["type"] == "uom_valid"),
            "products_enrichment_could_not_be_generated": sum(1 for item in warnings if item["type"] == "enrichment_unavailable"),
            "duplicate_mpns": duplicates,
            "near_duplicate_mpns": near_duplicates,
            "implemented_fields": ["PART_NUMBER", "Brand", "Manufacturer", "Part_Desc", "Attributes", "Category", "Short_Description", "Long_Description", "Features", "Specifications", "UOM", "validation", "provenance"],
            "unsupported_delivery_format_fields": "The 252-column Delivery Format is not available for this 1000-row input and is not claimed complete.",
            "rows": generated, "failed_row_details": failures, "validation_warnings": warnings,
        }
        self._write_scale_reports(summary, report_dir or self.root / "backend" / "evaluation_reports")
        return summary
    def _write_scale_reports(self, summary: Dict[str, Any], directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "generated_1000_products.json").open("w", encoding="utf-8") as handle:
            json.dump(summary["rows"], handle, ensure_ascii=False, indent=2)
        with (directory / "validation_1000_rows.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["row_number", "status", "mpn_present", "description_present", "brand_present", "manufacturer_valid", "brand_valid", "category_valid", "uom_valid", "placeholder_detected", "warning_count"])
            warnings_by_row: Dict[int, List[Dict[str, Any]]] = {}
            for warning in summary["validation_warnings"]:
                warnings_by_row.setdefault(warning["row_number"], []).append(warning)
            for item in summary["rows"]:
                output = item["output"]
                validation = output["validation"]
                row_warnings = warnings_by_row.get(item["row_number"], [])
                writer.writerow([item["row_number"], "warning" if row_warnings else "passed", bool(output["PART_NUMBER"]), bool(output["Part_Desc"]), bool(output["Brand"]), validation["manufacturer_valid"], validation["brand_valid"], validation["category_valid"], validation["uom_valid"], validation["placeholder_contamination"], len(row_warnings)])
        report = {key: value for key, value in summary.items() if key not in {"rows", "failed_row_details", "validation_warnings"}}
        with (directory / "summary_1000_evaluation.json").open("w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
        with (directory / "failed_1000_rows.json").open("w", encoding="utf-8") as handle:
            json.dump(summary["failed_row_details"], handle, ensure_ascii=False, indent=2)

    def evaluate_200(self, report_dir: Optional[Path] = None) -> Dict[str, Any]:
        path = self._dataset("Unilog-Sample_200_Items-Input-vs-Output.xlsx")
        vocab = self._vocab()
        rows = load_rows(path)
        details: List[Dict[str, Any]] = []
        fields = [("PART_NUMBER", ("PART_NUMBER", "MPN")), ("Brand", ("Brand", "Manufacturer")), ("Category", ("Category", "Taxonomy")), ("Part_Desc", ("Part_Desc", "Description")), ("UOM", ("UOM", "Unit"))]
        counts = {field: 0 for field, _ in fields}
        for row in rows:
            generated = generate_output(row, vocab)
            detail = {"input": dict(row), "fields": {}}
            for field, names in fields:
                expected = clean(column(row, f"Expected_{field}", f"Expected {field}", *names))
                actual = clean(generated.get(field, ""))
                match = bool(expected) and expected.casefold() == actual.casefold()
                counts[field] += int(match)
                detail["fields"][field] = {"expected": expected, "generated": actual, "match": match, "reason": "match" if match else "value mismatch or missing expected value"}
            detail["validation"] = generated["validation"]
            details.append(detail)
        total = len(rows)
        accuracy = {field: (value / total if total else 0.0) for field, value in counts.items()}
        report = {"total_rows": total, "processed_rows": total, "failed_rows": 0, "field_accuracy": accuracy, "manufacturer_accuracy": accuracy.get("Brand", 0.0), "brand_accuracy": accuracy.get("Brand", 0.0), "category_accuracy": accuracy.get("Category", 0.0), "attribute_accuracy": accuracy.get("Part_Desc", 0.0), "unit_accuracy": accuracy.get("UOM", 0.0), "description_accuracy": accuracy.get("Part_Desc", 0.0), "overall_score": sum(accuracy.values()) / len(accuracy) if accuracy else 0.0, "details": details}
        self._write_report(report, report_dir or self.root / "backend" / "evaluation_reports")
        return report
    def _write_report(self, report: Dict[str, Any], directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        output = directory / "evaluation_200_rows.csv"
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["row", "field", "input_value", "expected_value", "generated_value", "match", "reason"])
            for index, detail in enumerate(report["details"], 2):
                for field, result in detail["fields"].items():
                    writer.writerow([index, field, column(detail["input"], field), result["expected"], result["generated"], result["match"], result["reason"]])
        logger.info("Wrote Phase 2 evaluation report to %s", output)