"""Feature Engineering & Temporal Transformation Module for CropForecastLK.

Implements domain-specific yield ratios, temporal lag features, rolling statistics,
smoothed out-of-fold target encodings, and strict chronological train/val/test splits.
"""
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd
from ml_pipeline.config import (
    CLEANED_DATA_PATH,
    ENGINEERED_FEATURES_PATH,
    TRAIN_MAX_YEAR,
    VAL_MAX_YEAR,
    TEST_MAX_YEAR,
    RANDOM_STATE
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def compute_yield_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """Compute domain Crop_Yield (Metric Tons per Hectare).

    Crop_Yield = Production / Extent
    """
    df_out = df.copy()
    # Extent is in Hectares, Production in Metric Tons
    # Handle zero extent safely
    df_out["Crop_Yield"] = np.where(df_out["Extent"] > 0, df_out["Production"] / df_out["Extent"], 0.0)
    # Clip extreme outliers due to data entry division artifacts (yield > 100 MT/Ha is rare for highland field crops)
    df_out["Crop_Yield"] = df_out["Crop_Yield"].clip(upper=100.0)
    return df_out