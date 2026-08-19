from fastapi import APIRouter, HTTPException, status
from app.services.dataset_evaluation_service import DatasetEvaluationService
router = APIRouter(tags=["Evaluation"])
service = DatasetEvaluationService()

@router.post("/evaluate", status_code=status.HTTP_200_OK)
async def evaluate_dataset():
    try:
        return service.evaluate_200()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Dataset evaluation failed.") from exc
@router.post("/process-1000", status_code=status.HTTP_200_OK)
async def process_1000_dataset():
    try:
        return service.process("Unihack- Sample Dataset.xlsx")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="1000-item processing failed.") from exc
