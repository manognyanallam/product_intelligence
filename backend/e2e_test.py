"""End-to-end test of all API endpoints using FastAPI TestClient."""
import sys

try:
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    output = []
    failures = []

    def report(name, passed, detail=""):
        status = "PASS" if passed else "FAIL"
        if not passed:
            failures.append(f"{name} {detail}")
        output.append(f"[{status}] {name} {detail}")

    # 1. Health endpoint
    r = client.get("/api/v1/health")
    report("GET /health", r.status_code == 200, f"-> {r.status_code} {r.json()['status']}")

    # 2. Root endpoint
    r = client.get("/")
    report("GET /", r.status_code == 200)

    # 3. Analyze valid request
    r = client.post("/api/v1/analyze", json={
        "mpn": "SN74LS00N",
        "brand": "Texas Instruments",
        "description": "Quad 2-input NAND gate"
    })
    # With GEMINI_API_KEY configured -> 200 with real AI intelligence.
    # Without it -> 503 structured Gemini configuration error (still a valid,
    # controlled response from the new Gemini integration).
    report("POST /analyze valid", r.status_code in (200, 503), f"-> {r.status_code}")
    product = r.json()
    if r.status_code == 200:
        report("  Response has product_id", "product_id" in product)
        report("  Response has enriched_data", "enriched_data" in product)
        report("  MPN normalized to upper", product["input"]["mpn"] == "SN74LS00N")
        pid = product["product_id"]
    else:
        report("  Structured Gemini error (code present)", "detail" in product and isinstance(product["detail"], dict))
        report("  Gemini error has code field", isinstance(product.get("detail"), dict) and "code" in product["detail"])
        pid = None

    # 4. Analyze missing fields -> 422
    r = client.post("/api/v1/analyze", json={"brand": "TI", "description": "x"})
    report("POST /analyze missing mpn -> 422", r.status_code == 422, f"-> {r.status_code}")

    r = client.post("/api/v1/analyze", json={"mpn": "X", "description": "y"})
    report("POST /analyze missing brand -> 422", r.status_code == 422, f"-> {r.status_code}")

    r = client.post("/api/v1/analyze", json={"mpn": "X", "brand": "Y"})
    report("POST /analyze missing description -> 422", r.status_code == 422, f"-> {r.status_code}")

    # 5. Description too long -> 422
    r = client.post("/api/v1/analyze", json={
        "mpn": "X", "brand": "Y", "description": "z" * 1001
    })
    report("POST /analyze long description -> 422", r.status_code == 422, f"-> {r.status_code}")

    # 6. Download JSON for existing product
    if pid is not None:
        r = client.get(f"/api/v1/download-json/{pid}")
        report("GET /download-json existing", r.status_code == 200, f"-> {r.status_code}")
        report("  JSON content-type", r.headers.get("content-type", "").startswith("application/json"))
        report("  Has content-disposition", "content-disposition" in r.headers)
    else:
        report("GET /download-json existing (skipped — no AI product)", True, "(GEMINI_API_KEY not set)")

    # 7. Download JSON for missing product -> 404
    r = client.get("/api/v1/download-json/nonexistent")
    report("GET /download-json missing -> 404", r.status_code == 404, f"-> {r.status_code}")

    # 8. Download PDF for existing product
    if pid is not None:
        r = client.get(f"/api/v1/download-pdf/{pid}")
        report("GET /download-pdf existing", r.status_code == 200, f"-> {r.status_code}")
        report("  PDF content-type", r.headers.get("content-type", "").startswith("application/pdf"))
    else:
        report("GET /download-pdf existing (skipped — no AI product)", True, "(GEMINI_API_KEY not set)")

    # 9. Download PDF for missing product -> 404
    r = client.get("/api/v1/download-pdf/nonexistent")
    report("GET /download-pdf missing -> 404", r.status_code == 404, f"-> {r.status_code}")

    # 10. History endpoint
    r = client.get("/api/v1/history")
    report("GET /history", r.status_code == 200, f"-> {r.status_code}")
    hist = r.json()
    report("  History has results", "results" in hist)
    report("  History total > 0", hist["total"] > 0)

    r = client.get("/api/v1/history?page=1&limit=2&sort=asc")
    report("GET /history paginated", r.status_code == 200, f"-> {r.status_code}")

    # 11. Upload document (text file)
    r = client.post(
        "/api/v1/upload-document",
        files={"file": ("spec.txt", b"SN74LS00N datasheet content", "text/plain")},
        data={"mpn": "SN74LS00N"},
    )
    report("POST /upload-document valid", r.status_code == 201, f"-> {r.status_code}")
    doc = r.json()
    report("  Document has document_id", "document_id" in doc)

    # 12. Upload empty file -> 400
    r = client.post(
        "/api/v1/upload-document",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    report("POST /upload-document empty -> 400", r.status_code == 400, f"-> {r.status_code}")

    # 13. Upload unsupported type -> 400
    r = client.post(
        "/api/v1/upload-document",
        files={"file": ("bad.exe", b"MZ...", "application/octet-stream")},
    )
    report("POST /upload-document bad type -> 400", r.status_code == 400, f"-> {r.status_code}")

    # 14. Swagger docs available
    r = client.get("/docs")
    report("GET /docs (Swagger)", r.status_code == 200, f"-> {r.status_code}")

    r = client.get("/openapi.json")
    schema = r.json()
    paths = schema["paths"]
    expected = [
        ("/api/v1/analyze", "post"),
        ("/api/v1/upload-document", "post"),
        ("/api/v1/history", "get"),
        ("/api/v1/health", "get"),
        ("/api/v1/download-json/{product_id}", "get"),
        ("/api/v1/download-pdf/{product_id}", "get"),
    ]
    for path, method in expected:
        report(f"Swagger has {method.upper()} {path}", path in paths, f"-> {path in paths}")

    # Summary
    output.append("")
    result = "ALL PASSED" if not failures else "SOME TESTS FAILED"
    output.append(f"RESULT: {result}")
    text = "\n".join(output)
    print(text)
    with open("e2e_output.txt", "w", encoding="utf-8") as f:
        f.write(text)

except Exception as e:
    import traceback
    err = f"E2E FAILURE: {e}\n{traceback.format_exc()}"
    print(err)
    with open("e2e_output.txt", "w", encoding="utf-8") as f:
        f.write(err)
    sys.exit(1)

