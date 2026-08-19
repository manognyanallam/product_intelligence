# TODO — Gemini Integration for Product Intelligence Generation

- [x] 1. Update `backend/requirements.txt` — add latest official Google Generative AI SDK (`google-genai`)
- [x] 2. Create `backend/app/services/gemini_service.py` — GeminiService with structured exceptions, JSON-only prompt, retry-on-invalid-JSON, logging, metrics
- [x] 3. Update `backend/app/services/product_service.py` — integrate GeminiService into `analyze()`, map AI output to `ProductResponse`
- [x] 4. Update `backend/app/routers/product.py` — return structured API errors from `GeminiServiceError`
- [x] 5. Update `backend/app/routers/health.py` — report Gemini configuration status
- [x] 6. Update verification scripts (`verify_app.py`, `e2e_test.py`) for the new AI behavior
- [x] 7. Install dependencies and verify (`pip install -r requirements.txt`, run verify/e2e)

**Status:** All steps complete. Gemini integration implemented and verified.

