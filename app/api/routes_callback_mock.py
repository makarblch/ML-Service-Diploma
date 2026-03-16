from fastapi import APIRouter

router = APIRouter(tags=["mock-callback"])


@router.post("/mock/callbacks/predictions")
async def mock_prediction_callback(payload: dict) -> dict:
    print("CALLBACK RECEIVED:", payload)
    return {"status": "ok"}