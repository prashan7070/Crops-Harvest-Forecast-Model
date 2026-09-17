"""Analytics & Historical Agronomic Intelligence Endpoints."""
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from fastapi import APIRouter, HTTPException, Query, status

from backend.app.core.config import settings
from backend.app.core.model_loader import model_loader

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory cached historical data
_cached_historical_df: Optional[pd.DataFrame] = None


def get_historical_df() -> pd.DataFrame:
    global _cached_historical_df
    if _cached_historical_df is None:
        if settings.CLEANED_DATA_PATH.exists():
            df = pd.read_csv(settings.CLEANED_DATA_PATH)
            # Add yield column
            df["Crop_Yield"] = df.apply(
                lambda r: round(r["Production"] / r["Extent"], 3) if r["Extent"] > 0 else 0.0,
                axis=1
            )
            _cached_historical_df = df
        else:
            _cached_historical_df = pd.DataFrame(columns=["District", "Crop", "Season", "Year", "Extent", "Production", "Crop_Yield"])
    return _cached_historical_df


@router.get("/districts", summary="Get Available Districts and Agronomic Summaries")
async def get_districts():
    df = get_historical_df()
    target_crops = model_loader.metadata.get("supported_crops", [
        "Potato", "Maize", "Kurakkan", "Chili", "Cassava", "Sweet Potato", "Green Gram"
    ])

    if df.empty:
        districts = model_loader.metadata.get("supported_highland_districts", [])
        return {"districts": districts, "summaries": []}

    target_df = df[df["Crop"].isin(target_crops)]
    raw_districts = sorted(target_df["District"].dropna().unique().tolist())
    
    highland_districts = model_loader.metadata.get("supported_highland_districts", [])
    if highland_districts:
        districts = [d for d in raw_districts if d in highland_districts]
    else:
        districts = raw_districts

    summaries = []
    for d in districts:
        d_df = target_df[target_df["District"] == d]
        summaries.append({
            "district": d,
            "total_records": len(d_df),
            "available_crops": sorted(d_df["Crop"].dropna().unique().tolist()),
            "avg_extent_ha": round(float(d_df["Extent"].mean()), 2),
            "avg_production_mt": round(float(d_df["Production"].mean()), 2),
            "avg_yield_mt_per_ha": round(float(d_df["Crop_Yield"].mean()), 3),
        })

    return {
        "districts": districts,
        "highland_districts": model_loader.metadata.get("supported_highland_districts", []),
        "summaries": summaries
    }


@router.get("/crops", summary="Get Supported Highland Crops")
async def get_crops():
    df = get_historical_df()
    all_crops = sorted(df["Crop"].dropna().unique().tolist()) if not df.empty else []
    target_crops = model_loader.metadata.get("supported_crops", [
        "Potato", "Maize", "Kurakkan", "Chili", "Cassava", "Sweet Potato", "Green Gram"
    ])
    return {
        "crops": all_crops,
        "highland_target_crops": target_crops
    }


@router.get("/trends", summary="Historical Time-Series Production & Yield Trends")
async def get_historical_trends(
    district: str = Query(..., examples=["Nuwara Eliya"]),
    crop: str = Query(..., examples=["Potato"])
):
    """Retrieve historical time series data for Recharts seasonal charts."""
    df = get_historical_df()
    if df.empty:
        return {"points": []}

    subset = df[
        (df["District"].str.lower() == district.strip().lower()) &
        (df["Crop"].str.lower() == crop.strip().lower())
    ].sort_values(by=["Year", "Season"]).copy()

    points = []
    for _, row in subset.iterrows():
        points.append({
            "year": int(row["Year"]),
            "season": str(row["Season"]),
            "extent_ha": round(float(row["Extent"]), 2),
            "production_mt": round(float(row["Production"]), 2),
            "yield_mt_per_ha": round(float(row["Crop_Yield"]), 3),
        })

    return {
        "district": district,
        "crop": crop,
        "total_records": len(points),
        "data": points
    }


@router.get("/model-stats", summary="Model Performance Benchmarks & Metadata")
async def get_model_stats():
    """Retrieve model metadata, benchmark evaluation scores, and Optuna parameters."""
    metadata = model_loader.metadata
    return {
        "metadata": metadata,
        "features": metadata.get("features", []),
        "metrics": metadata.get("metrics", {}),
        "best_hyperparameters": metadata.get("best_hyperparameters", {})
    }
