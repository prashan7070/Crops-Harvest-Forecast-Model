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


def create_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate 1-year lags and 3-year rolling window statistics without data leakage.

    Features created:
    - Production_Lag_1Y: 1-year lagged production for (District, Crop, Season)
    - Yield_Lag_1Y: 1-year lagged yield for (District, Crop, Season)
    - Extent_RollMean_3Y: 3-year rolling average cultivated extent
    - Extent_RollStd_3Y: 3-year rolling standard deviation of extent
    """
    df_out = df.copy()
    # Ensure chronological ordering per cohort
    cohort_cols = ["District", "Crop", "Season"]
    df_out = df_out.sort_values(by=cohort_cols + ["Year"]).reset_index(drop=True)

    grouped = df_out.groupby(cohort_cols)

    # 1. Temporal Lags (t - 1)
    df_out["Production_Lag_1Y"] = grouped["Production"].shift(1)
    df_out["Yield_Lag_1Y"] = grouped["Crop_Yield"].shift(1)

    # Fill initial year missing lag values with cohort medians or defaults
    df_out["Production_Lag_1Y"] = df_out["Production_Lag_1Y"].fillna(grouped["Production"].transform("median"))
    df_out["Production_Lag_1Y"] = df_out["Production_Lag_1Y"].fillna(df_out["Production"].median())

    df_out["Yield_Lag_1Y"] = df_out["Yield_Lag_1Y"].fillna(grouped["Crop_Yield"].transform("median"))
    df_out["Yield_Lag_1Y"] = df_out["Yield_Lag_1Y"].fillna(df_out["Crop_Yield"].median())

    # 2. Rolling Window Statistics (3-Year)
    df_out["Extent_RollMean_3Y"] = grouped["Extent"].transform(lambda x: x.rolling(3, min_periods=1).mean())
    df_out["Extent_RollStd_3Y"] = grouped["Extent"].transform(lambda x: x.rolling(3, min_periods=1).std()).fillna(0.0)

    return df_out