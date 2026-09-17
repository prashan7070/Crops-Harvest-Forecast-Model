"""Health & Service Readiness Endpoint."""
from fastapi import APIRouter
from backend.app.schemas.prediction import HealthResponse
from backend.app.core.model_loader import model_loader

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Service Health & Model Status")
async def health_check():
    metadata = model_loader.metadata
    return {
        "status": "online",
        "model_loaded": model_loader.is_loaded,
        "model_version": metadata.get("version", "1.0.0"),
        "model_type": metadata.get("model_type", "XGBoost"),
        "available_districts_count": len(metadata.get("all_districts", [])),
        "available_crops_count": len(metadata.get("all_crops", []))
    }
