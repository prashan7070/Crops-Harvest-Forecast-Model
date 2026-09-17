"""Prediction Endpoints for CropForecastLK."""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse
)
from backend.app.core.model_loader import model_loader

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict Harvest Production & Yield for a Single Parcel"
)
async def predict_harvest(request: PredictionRequest):
    """Predict seasonal crop production (Metric Tons) and yield (MT/Ha).

    - **district**: Sri Lankan district (e.g. Nuwara Eliya, Badulla, Kandy, Matale, Moneragala)
    - **season**: 'Maha' or 'Yala'
    - **crop**: Highland agricultural crop (e.g. Potato, Maize, Kurakkan, Chili, Cassava, Sweet Potato)
    - **extent_ha**: Cultivated land area in Hectares (> 0)
    - **year**: Harvest forecast year (default: 2024)
    """
    if not model_loader.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Predictive inference pipeline is still initializing or unavailable."
        )

    try:
        result = model_loader.predict(
            district=request.district,
            season=request.season,
            crop=request.crop,
            extent_ha=request.extent_ha,
            year=request.year or 2024
        )
        return result
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )


@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch Harvest Forecast Scenarios"
)
async def predict_batch_harvest(request: BatchPredictionRequest):
    """Execute batch forecasts across multiple district-crop-extent combinations."""
    if not model_loader.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Predictive inference pipeline is still initializing."
        )

    try:
        scenarios_dicts = [s.model_dump() for s in request.scenarios]
        predictions = model_loader.predict_batch(scenarios_dicts)
        return {
            "count": len(predictions),
            "predictions": predictions
        }
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch inference error: {str(e)}"
        )
