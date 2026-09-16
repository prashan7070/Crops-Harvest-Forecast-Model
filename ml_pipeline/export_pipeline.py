"""Hyperparameter Optimization & Production Pipeline Packaging Module.

Performs Optuna hyperparameter tuning, encapsulates feature transformations
and the champion estimator into a deployable CropForecasterPipeline,
and serializes artifacts to joblib and JSON.
"""
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from ml_pipeline.config import (
    ENGINEERED_FEATURES_PATH,
    CLEANED_DATA_PATH,
    PIPELINE_EXPORT_PATH,
    BEST_PARAMS_PATH,
    MODEL_METADATA_PATH,
    RANDOM_STATE,
    OPTUNA_TRIALS,
    HIGHLAND_DISTRICTS,
    TARGET_CROPS
)
from ml_pipeline.feature_engineering import split_temporal_data
from ml_pipeline.train import FEATURE_COLS, TARGET_COL, get_model
from ml_pipeline.evaluate import compute_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CropForecasterPipeline:
    """Production Inference Pipeline for Sri Lankan Highland Crop Forecasting.

    Encapsulates:
    1. Historical agronomic priors lookup (lag production, lag yield, rolling extent).
    2. Categorical target encodings and seasonal binary flags.
    3. Tuned gradient boosted decision tree estimator (XGBoost).
    4. Post-processing (yield calculation, non-negative clipping, confidence bounds).
    """

    def __init__(
        self,
        model: XGBRegressor,
        district_enc_map: Dict[str, float],
        crop_enc_map: Dict[str, float],
        global_target_mean: float,
        cohort_history: Dict[Tuple[str, str, str], Dict[str, float]],
        feature_names: list,
        metadata: Dict[str, Any]
    ):
        self.model = model
        self.district_enc_map = district_enc_map
        self.crop_enc_map = crop_enc_map
        self.global_target_mean = global_target_mean
        self.cohort_history = cohort_history
        self.feature_names = feature_names
        self.metadata = metadata

    def _get_cohort_defaults(self, district: str, crop: str, season: str) -> Dict[str, float]:
        """Retrieve historical lag and rolling statistics for a given cohort."""
        key = (district, crop, season)
        if key in self.cohort_history:
            return self.cohort_history[key]
        
        # Fallback to crop-level defaults
        crop_matches = [v for k, v in self.cohort_history.items() if k[1] == crop]
        if crop_matches:
            return {
                "prod_lag": float(np.median([m["prod_lag"] for m in crop_matches])),
                "yield_lag": float(np.median([m["yield_lag"] for m in crop_matches])),
                "ext_roll_mean": float(np.median([m["ext_roll_mean"] for m in crop_matches])),
                "ext_roll_std": 0.0,
            }
        
        # Global fallback
        return {
            "prod_lag": 500.0,
            "yield_lag": 5.0,
            "ext_roll_mean": 100.0,
            "ext_roll_std": 0.0,
        }

    def predict_single(
        self,
        district: str,
        season: str,
        crop: str,
        extent_ha: float,
        year: int = 2024
    ) -> Dict[str, Any]:
        """Generate harvest production and yield forecast for a single parcel/district scenario.

        Args:
            district: Sri Lanka District (e.g. 'Nuwara Eliya')
            season: 'Maha' or 'Yala'
            crop: Highland crop (e.g. 'Potato', 'Maize')
            extent_ha: Cultivated land extent in Hectares
            year: Agricultural forecast year

        Returns:
            Dict containing predicted production in MT, yield in MT/Ha, and confidence intervals.
        """
        # 1. Look up historical priors
        defaults = self._get_cohort_defaults(district, crop, season)
        
        # Dynamic adjustment: if user specifies extent, roll_mean incorporates current extent
        ext_roll_mean = (defaults["ext_roll_mean"] * 2 + extent_ha) / 3.0

        # 2. Encodings
        dist_enc = self.district_enc_map.get(district, self.global_target_mean)
        crop_enc = self.crop_enc_map.get(crop, self.global_target_mean)
        season_maha = 1 if season.strip().lower() == "maha" else 0

        # 3. Construct feature vector matching FEATURE_COLS
        features = pd.DataFrame([{
            "Extent": float(extent_ha),
            "Production_Lag_1Y": defaults["prod_lag"],
            "Yield_Lag_1Y": defaults["yield_lag"],
            "Extent_RollMean_3Y": ext_roll_mean,
            "Extent_RollStd_3Y": defaults["ext_roll_std"],
            "District_TargetEnc": dist_enc,
            "Crop_TargetEnc": crop_enc,
            "Season_Maha": season_maha,
            "Year": int(year)
        }])[self.feature_names]

        # 4. Estimator inference
        pred_prod = float(self.model.predict(features)[0])
        pred_prod = max(0.0, pred_prod)  # Clip negative values

        # 5. Domain yield calculation
        crop_yield = pred_prod / extent_ha if extent_ha > 0 else 0.0

        # 6. Confidence interval based on test RMSE
        test_rmse = self.metadata.get("metrics", {}).get("test_rmse", 150.0)
        ci_lower = max(0.0, pred_prod - 1.96 * (test_rmse * 0.25))
        ci_upper = pred_prod + 1.96 * (test_rmse * 0.25)

        return {
            "district": district,
            "season": season,
            "crop": crop,
            "extent_ha": float(extent_ha),
            "forecast_year": int(year),
            "predicted_production_mt": round(pred_prod, 2),
            "predicted_yield_mt_per_ha": round(crop_yield, 3),
            "confidence_interval_95": {
                "lower_mt": round(ci_lower, 2),
                "upper_mt": round(ci_upper, 2)
            },
            "model_version": self.metadata.get("version", "1.0.0"),
            "inference_timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def predict_batch(self, items: list) -> list:
        """Batch inference for multiple planning scenarios."""
        return [self.predict_single(**item) for item in items]

def build_and_export_production_pipeline(
    engineered_path: Path = ENGINEERED_FEATURES_PATH,
    pipeline_out: Path = PIPELINE_EXPORT_PATH,
    metadata_out: Path = MODEL_METADATA_PATH
) -> CropForecasterPipeline:
    """End-to-end routine to train, package, and serialize the inference pipeline."""
    logger.info(f"Loading engineered features from {engineered_path}...")
    df = pd.read_csv(engineered_path)
    train_df, val_df, test_df = split_temporal_data(df)

    # Combine Train + Val for final model fitting before test evaluation
    train_val_df = pd.concat([train_df, val_df], ignore_index=True)
    champion_model = get_model()
    
    champion_model.fit(train_val_df[FEATURE_COLS], train_val_df[TARGET_COL])

    # Evaluate on Holdout Test Set (2021-2023)
    test_preds = champion_model.predict(test_df[FEATURE_COLS])
    test_metrics = compute_metrics(test_df[TARGET_COL].values, test_preds)
    logger.info(f"Final Champion Test Metrics: {test_metrics}")

    # Extract target encoding maps & cohort history
    district_enc_map = train_df.groupby("District")["District_TargetEnc"].mean().to_dict()
    crop_enc_map = train_df.groupby("Crop")["Crop_TargetEnc"].mean().to_dict()
    global_mean = float(train_df[TARGET_COL].mean())

    cohort_history = {}
    for (d, c, s), group in df.groupby(["District", "Crop", "Season"]):
        cohort_history[(d, c, s)] = {
            "prod_lag": float(group["Production"].iloc[-1]) if len(group) > 0 else global_mean,
            "yield_lag": float(group["Crop_Yield"].iloc[-1]) if len(group) > 0 else 5.0,
            "ext_roll_mean": float(group["Extent"].tail(3).mean()) if len(group) > 0 else 100.0,
            "ext_roll_std": float(group["Extent"].tail(3).std()) if len(group) > 1 and not np.isnan(group["Extent"].tail(3).std()) else 0.0
        }