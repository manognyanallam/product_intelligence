"""Verify the FastAPI application boots correctly and all endpoints register."""
import sys
import io
import json

# Capture any errors
try:
    from app.main import app
    routes = [f"{sorted(r.methods)[0] if hasattr(r, 'methods') and r.methods else 'GET':6s} {r.path}" for r in app.routes if hasattr(r, 'path')]
    
    output = []
    output.append("=== APP BOOT VERIFICATION ===")
    output.append(f"App title: {app.title}")
    output.append(f"App version: {app.version}")
    output.append("")
    output.append("=== REGISTERED ROUTES ===")
    for route in routes:
        output.append(route)
    output.append("")
    
    # Test the health endpoint logic directly
    from app.routers.health import _START_TIME
    output.append(f"Health _START_TIME set: {_START_TIME > 0}")
    
    # Test ProductRequest validation
    from app.schemas.request import ProductRequest
    from pydantic import ValidationError
    
    # Valid request
    req = ProductRequest(mpn="SN74LS00N", brand="TI", description="Quad NAND")
    output.append(f"Valid ProductRequest OK: mpn={req.mpn}")
    
    # Missing mpn -> should raise
    try:
        ProductRequest(brand="TI", description="test")
        output.append("FAIL: Missing mpn did not raise ValidationError")
    except ValidationError as e:
        output.append(f"PASS: Missing mpn raises 422 -> {e.errors()[0]['loc']}")
    
    # Description too long
    try:
        ProductRequest(mpn="X", brand="Y", description="x" * 1001)
        output.append("FAIL: Long description did not raise ValidationError")
    except ValidationError as e:
        output.append(f"PASS: Long description raises 422 -> {e.errors()[0]['type']}")
    
    # Missing brand
    try:
        ProductRequest(mpn="X", description="test")
        output.append("FAIL: Missing brand did not raise ValidationError")
    except ValidationError as e:
        output.append(f"PASS: Missing brand raises 422 -> {e.errors()[0]['loc']}")
    
    # Test ProductService with Gemini integration
    import asyncio
    from app.services.product_service import ProductService
    from app.services.gemini_service import GeminiServiceError, GeminiConfigurationError
    from app.schemas.request import ProductRequest as PR

    async def test_service():
        service = ProductService()
        try:
            result = await service.analyze(PR(mpn="SN74LS00N", brand="Texas Instruments", description="Quad 2-input NAND gate"))
            output.append(f"ProductService.analyze OK: product_id={result.product_id}")
            output.append(f"  Enriched MPN: {result.enriched_data.mpn}")
            output.append(f"  Overall confidence: {result.confidence.overall}")
            output.append(f"  Intelligence agent status: {result.agent_timeline[1].status}")
            return result
        except GeminiConfigurationError as exc:
            output.append(f"ProductService.analyze (no GEMINI_API_KEY) -> GeminiConfigurationError: {exc.message}")
            output.append("  (Expected when GEMINI_API_KEY is not set; set it in .env to run the full AI pipeline.)")
            return None

    result = asyncio.run(test_service())

    # Test GeminiService error handling when no API key is configured
    from app.core.config import settings as app_settings
    if not app_settings.gemini_api_key:
        from app.services.gemini_service import GeminiService as GS
        async def test_gemini_no_key():
            gs = GS()
            try:
                await gs.generate_product_intelligence(mpn="SN74LS00N", brand="TI", description="NAND gate")
                output.append("FAIL: GeminiService did not raise without API key")
            except GeminiServiceError as e:
                output.append(f"PASS: GeminiService raises {type(e).__name__} without API key (status={e.status_code})")
        asyncio.run(test_gemini_no_key())

    # Test PDF generation
    async def test_pdf():
        from app.services.export_service import ExportService
        if result is None:
            # Build a minimal ProductResponse from ProductService mock-free path
            from app.schemas.response import ProductResponse, ProductInput, EnrichedData, ConfidenceScore, ValidationReport
            fallback = ProductResponse(
                product_id="prod_test_000001",
                status="completed",
                input=ProductInput(mpn="SN74LS00N", brand="TI", description="NAND"),
                enriched_data=EnrichedData(mpn="SN74LS00N", brand="TI", manufacturer="TI", title="SN74LS00N"),
                confidence=ConfidenceScore(overall=0.5),
                validation=ValidationReport(),
            )
            pdf = await ExportService().generate_pdf(fallback)
        else:
            pdf = await ExportService().generate_pdf(result)
        output.append(f"PDF generation OK: {len(pdf)} bytes, starts with %PDF: {pdf[:4] == b'%PDF'}")
    
    asyncio.run(test_pdf())
    
    # Test HistoryService
    async def test_history():
        from app.services.history_service import HistoryService
        hist = await HistoryService().get_history()
        output.append(f"HistoryService OK: {hist.total} entries")
    
    asyncio.run(test_history())
    
    output_text = "\n".join(output)
    print(output_text)
    with open("verify_output.txt", "w", encoding="utf-8") as f:
        f.write(output_text)
    print("WROTE verify_output.txt")
    
except Exception as e:
    import traceback
    err = f"BOOT FAILURE: {e}\n{traceback.format_exc()}"
    print(err)
    with open("verify_output.txt", "w", encoding="utf-8") as f:
        f.write(err)
    sys.exit(1)

