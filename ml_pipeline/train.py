"""Model Training, Multi-Model Benchmarking & Time-Series Cross-Validation Module.

Benchmarks 5 diverse regression algorithms:
1. Ridge Regression (Linear baseline)
2. Random Forest Regressor (Bagging ensemble)
3. LightGBM Regressor (Leaf-wise gradient boosting)
4. CatBoost Regressor (Symmetric gradient boosting)
5. XGBoost Regressor (Depth-wise regularized gradient boosting)
"""
import logging
import time
from pathlib import Path
from typing import Dict, Any, Tuple, List
import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from ml_pipeline.config import (
    ENGINEERED_FEATURES_PATH,
    RANDOM_STATE,
    TRAIN_MAX_YEAR,
    VAL_MAX_YEAR,
    TEST_MAX_YEAR
)
from ml_pipeline.evaluate import compute_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

FEATURE_COLS = [
    "Extent",
    "Production_Lag_1Y",
    "Yield_Lag_1Y",
    "Extent_RollMean_3Y",
    "Extent_RollStd_3Y",
    "District_TargetEnc",
    "Crop_TargetEnc",
    "Season_Maha",
    "Year"
]

TARGET_COL = "Production"


def get_model(random_state: int = RANDOM_STATE) -> Any:
    """Instantiate the XGBoost regression model."""
    return XGBRegressor(
        n_estimators=150,
        learning_rate=0.08,
        max_depth=6,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=random_state,
        n_jobs=-1
    )