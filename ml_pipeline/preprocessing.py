"""Data Preprocessing & Cleaning Module for CropForecastLK.

Implements regex parsing of numeric columns, filtering of aggregate rows,
biological anomaly correction, and localized group-median imputation.
"""
import logging
import re
from pathlib import Path
from typing import Optional, Union, Any
import numpy as np
import pandas as pd
from ml_pipeline.config import RAW_DATA_PATH, CLEANED_DATA_PATH, HIGHLAND_DISTRICTS, TARGET_CROPS

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clean_numeric_string(val: Any) -> float:
    """Sanitize string values containing commas, hyphens, and text placeholders to float.

    Args:
        val: Raw string, float, or NaN.

    Returns:
        Cleaned float value or np.nan.
    """
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    if val_str in ["-", "n.a.", "nan", "", "None", "NULL", "null", "."]:
        return np.nan

    # Remove commas, whitespace, and any non-numeric character except decimal point
    clean_str = re.sub(r"[^\d.]", "", val_str)
    if not clean_str:
        return np.nan
    try:
        return float(clean_str)
    except ValueError:
        return np.nan


def clean_year_string(val: Any) -> Optional[int]:
    """Parse calendar or split agricultural year strings into an integer year.

    For split seasons (e.g. '2000/2001'), we take the concluding harvest year (2001).

    Args:
        val: String or integer year representation.

    Returns:
        Integer year or None.
    """
    if pd.isna(val):
        return None
    val_str = str(val).strip()
    if "/" in val_str:
        parts = val_str.split("/")
        val_str = parts[-1].strip()
    try:
        return int(float(val_str))
    except ValueError:
        return None


def filter_aggregate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Filter out national summary rows and aggregate season totals.

    Args:
        df: Input DataFrame.

    Returns:
        DataFrame containing only district-level and single-season records.
    """
    initial_count = len(df)
    aggregates = ["national total", "island total", "total", "all districts"]

    # Filter out district aggregate rows
    df_clean = df[~df["District"].astype(str).str.lower().str.strip().isin(aggregates)].copy()

    # Filter out season totals ('Total' represents sum of Maha and Yala)
    df_clean = df_clean[df_clean["Season"].astype(str).str.lower().str.strip().isin(["maha", "yala"])].copy()

    filtered_count = initial_count - len(df_clean)
    logger.info(f"Filtered out {filtered_count:,} aggregate rows (remaining: {len(df_clean):,}).")
    return df_clean


