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

def time_series_cv(
    model: Any,
    train_df: pd.DataFrame,
    n_splits: int = 5
) -> Dict[str, float]:
    """Execute expanding-window Time-Series Cross-Validation across the Year dimension.

    Folds expand chronologically:
    Fold 1: Train 2000-2005 -> Val 2006-2008
    Fold 2: Train 2000-2008 -> Val 2009-2011
    Fold 3: Train 2000-2011 -> Val 2012-2013
    Fold 4: Train 2000-2013 -> Val 2014-2015
    Fold 5: Train 2000-2015 -> Val 2016-2017
    """
    years = sorted(train_df["Year"].unique())
    min_year, max_year = years[0], years[-1]
    
    # 5 expanding window test slices
    val_slices = [
        (min_year, 2005, 2006, 2008),
        (min_year, 2008, 2009, 2011),
        (min_year, 2011, 2012, 2013),
        (min_year, 2013, 2014, 2015),
        (min_year, 2015, 2016, 2017),
    ]

    rmse_list, mae_list, r2_list = [], [], []

    for tr_start, tr_end, val_start, val_end in val_slices:
        fold_train = train_df[(train_df["Year"] >= tr_start) & (train_df["Year"] <= tr_end)]
        fold_val = train_df[(train_df["Year"] >= val_start) & (train_df["Year"] <= val_end)]

        X_tr = fold_train[FEATURE_COLS]
        y_tr = fold_train[TARGET_COL]
        X_v = fold_val[FEATURE_COLS]
        y_v = fold_val[TARGET_COL]

        model.fit(X_tr, y_tr)
        preds = model.predict(X_v)
        metrics = compute_metrics(y_v.values, preds)

        rmse_list.append(metrics["rmse"])
        mae_list.append(metrics["mae"])
        r2_list.append(metrics["r2"])

    return {
        "cv_rmse_mean": round(float(np.mean(rmse_list)), 2),
        "cv_rmse_std": round(float(np.std(rmse_list)), 2),
        "cv_mae_mean": round(float(np.mean(mae_list)), 2),
        "cv_r2_mean": round(float(np.mean(r2_list)), 4)
    }

def train_and_evaluate(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame
) -> Tuple[Any, Dict[str, Any]]:
    """Train XGBoost model and evaluate across Test sets.

    Returns:
        Tuple of (fitted_model, test_metrics).
    """
    model = get_model()

    X_train = train_df[FEATURE_COLS]
    y_train = train_df[TARGET_COL]
    X_test = test_df[FEATURE_COLS]
    y_test = test_df[TARGET_COL]

    logger.info("Training XGBoost Regressor...")
    model.fit(X_train, y_train)

    logger.info("Evaluating on Holdout Test set...")
    test_preds = model.predict(X_test)
    test_metrics = compute_metrics(y_test.values, test_preds)

    return model, test_metrics


if __name__ == "__main__":
    df = pd.read_csv(ENGINEERED_FEATURES_PATH)
    from ml_pipeline.feature_engineering import split_temporal_data
    tr, va, te = split_temporal_data(df)
    model, test_metrics = train_and_evaluate(tr, va, te)
    print("\n--- Final Test Set Results ---")
    print(f"RMSE: {test_metrics['rmse']} MT")
    print(f"R²:   {test_metrics['r2']}")
