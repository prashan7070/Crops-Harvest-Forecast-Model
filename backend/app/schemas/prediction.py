"""Pydantic Request & Response Validation Schemas."""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ConfidenceInterval(BaseModel):
    lower_mt: float = Field(..., description="95% CI Lower Bound (Metric Tons)")
    upper_mt: float = Field(..., description="95% CI Upper Bound (Metric Tons)")


class PredictionRequest(BaseModel):
    district: str = Field(..., example="Nuwara Eliya", description="Sri Lanka District name")
    season: str = Field(..., example="Maha", description="Maha or Yala agricultural season")
    crop: str = Field(..., example="Potato", description="Highland crop type")
    extent_ha: float = Field(..., gt=0, example=250.0, description="Cultivated land extent in Hectares")
    year: Optional[int] = Field(2024, ge=2000, le=2035, example=2024, description="Harvest forecast year")


class PredictionResponse(BaseModel):
    district: str
    season: str
    crop: str
    extent_ha: float
    forecast_year: int
    predicted_production_mt: float = Field(..., description="Forecasted Harvest Production in Metric Tons")
    predicted_yield_mt_per_ha: float = Field(..., description="Calculated Crop Yield in MT per Hectare")
    confidence_interval_95: ConfidenceInterval
    model_version: str
    inference_timestamp: str


class BatchPredictionRequest(BaseModel):
    scenarios: List[PredictionRequest]


class BatchPredictionResponse(BaseModel):
    count: int
    predictions: List[PredictionResponse]


class HistoricalTrendPoint(BaseModel):
    year: int
    season: str
    extent: float
    production: float
    yield_mt_per_ha: float


class DistrictSummary(BaseModel):
    district: str
    total_records: int
    available_crops: List[str]
    historical_avg_production_mt: float
    historical_avg_yield_mt_per_ha: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    model_type: str
    available_districts_count: int
    available_crops_count: int
