"""Evaluation and Diagnostics Module for CropForecastLK.

Implements standardized regression metrics (RMSE, MAE, R2, MAPE),
residual analysis plots, and SHAP explainability utilities.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute standardized regression evaluation metrics.

    Args:
        y_true: Ground truth target values (Metric Tons).
        y_pred: Predicted target values (Metric Tons).

    Returns:
        Dict containing RMSE, MAE, R2, and MAPE.
    """
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)

    # Ensure predictions are non-negative for production
    y_p = np.clip(y_p, a_min=0, a_max=None)

    rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))
    mae = float(mean_absolute_error(y_t, y_p))
    r2 = float(r2_score(y_t, y_p))

    return {
        "rmse": round(rmse, 2),
        "mae": round(mae, 2),
        "r2": round(r2, 4)
    }


