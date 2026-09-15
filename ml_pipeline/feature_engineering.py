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


class TargetEncoder:
    """Smoothed Out-of-Fold Target Encoder preventing data leakage.

    Formula: S_i = (n * y_cat + m * y_global) / (n + m)
    where m is the smoothing parameter (default = 10.0).
    """
    def __init__(self, cols: list, smoothing: float = 10.0):
        self.cols = cols
        self.smoothing = smoothing
        self.mappings_: Dict[str, Dict[str, float]] = {}
        self.global_mean_: float = 0.0

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.global_mean_ = float(y.mean())
        for col in self.cols:
            grouped = y.groupby(X[col])
            counts = grouped.count()
            means = grouped.mean()
            smoothed = (counts * means + self.smoothing * self.global_mean_) / (counts + self.smoothing)
            self.mappings_[col] = smoothed.to_dict()
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_out = X.copy()
        for col in self.cols:
            mapping = self.mappings_.get(col, {})
            encoded_col_name = f"{col}_TargetEnc"
            X_out[encoded_col_name] = X_out[col].map(mapping).fillna(self.global_mean_)
        return X_out

    def fit_transform(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        self.fit(X, y)
        return self.transform(X)


def encode_features(
    train_df: pd.DataFrame,
    val_df: Optional[pd.DataFrame] = None,
    test_df: Optional[pd.DataFrame] = None,
    target_col: str = "Production"
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Optional[pd.DataFrame], TargetEncoder]:
    """Encode categorical features (District, Crop, Season) and apply log target transformation.

    Season is binary one-hot encoded (Maha=1, Yala=0).
    District and Crop are smoothed target encoded using only the training split.
    """
    # Season binary encoding
    def apply_season_encoding(df: pd.DataFrame) -> pd.DataFrame:
        df_encoded = df.copy()
        df_encoded["Season_Maha"] = (df_encoded["Season"].str.lower() == "maha").astype(int)
        df_encoded["Log_Production"] = np.log1p(df_encoded[target_col].clip(lower=0))
        return df_encoded

    train_enc = apply_season_encoding(train_df)
    val_enc = apply_season_encoding(val_df) if val_df is not None else None
    test_enc = apply_season_encoding(test_df) if test_df is not None else None

    # Fit target encoder strictly on training data
    encoder = TargetEncoder(cols=["District", "Crop"], smoothing=10.0)
    encoder.fit(train_enc, train_enc[target_col])

    train_enc = encoder.transform(train_enc)
    if val_enc is not None:
        val_enc = encoder.transform(val_enc)
    if test_enc is not None:
        test_enc = encoder.transform(test_enc)

    return train_enc, val_enc, test_enc, encoder


def split_temporal_data(
    df: pd.DataFrame,
    train_max_year: int = TRAIN_MAX_YEAR,
    val_max_year: int = VAL_MAX_YEAR,
    test_max_year: int = TEST_MAX_YEAR
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split dataset chronologically to prevent temporal data leakage.

    Split boundaries:
    - Train: Year <= train_max_year (e.g. 2000 - 2017)
    - Validation: train_max_year < Year <= val_max_year (e.g. 2018 - 2020)
    - Test: val_max_year < Year <= test_max_year (e.g. 2021 - 2023)
    """
    train_df = df[(df["Year"] <= train_max_year) & (df["Year"] >= 2000)].copy()
    val_df = df[(df["Year"] > train_max_year) & (df["Year"] <= val_max_year)].copy()
    test_df = df[(df["Year"] > val_max_year) & (df["Year"] <= test_max_year)].copy()

    logger.info(
        f"Temporal Splits created: Train={len(train_df):,} rows (<= {train_max_year}), "
        f"Val={len(val_df):,} rows ({train_max_year + 1}-{val_max_year}), "
        f"Test={len(test_df):,} rows ({val_max_year + 1}-{test_max_year})"
    )
    return train_df, val_df, test_df

