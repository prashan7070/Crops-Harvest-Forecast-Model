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


def handle_anomalies_and_impute(df: pd.DataFrame) -> pd.DataFrame:
    """Handle impossible biological records and perform group-median imputation.

    Agronomic Rule:
    - Extent == 0 and Production > 0: Biologically impossible; set Production to NaN.
    - Extent > 0 and Production == 0: Valid crop failure scenario; preserved.

    Group-median imputation:
    - Impute missing values based on (District, Crop, Season) cohorts.
    - Fallback to (Crop, Season) median, then global Crop median.

    Args:
        df: DataFrame with cleaned numeric columns.

    Returns:
        Imputed DataFrame.
    """
    df_out = df.copy()

    # Rule 1: Zero extent with positive production
    mask_impossible = (df_out["Extent"] == 0) & (df_out["Production"] > 0)
    if mask_impossible.sum() > 0:
        logger.info(f"Identified {mask_impossible.sum()} impossible records (Extent=0, Production>0). Setting Production to NaN.")
        df_out.loc[mask_impossible, "Production"] = np.nan

    # Group-wise median imputation
    cohort_cols = ["District", "Crop", "Season"]
    for col in ["Extent", "Production"]:
        # 1st level: District + Crop + Season median
        median_cohort = df_out.groupby(cohort_cols)[col].transform("median")
        df_out[col] = df_out[col].fillna(median_cohort)

        # 2nd level: Crop + Season median
        median_crop_season = df_out.groupby(["Crop", "Season"])[col].transform("median")
        df_out[col] = df_out[col].fillna(median_crop_season)

        # 3rd level: Global Crop median
        median_crop = df_out.groupby("Crop")[col].transform("median")
        df_out[col] = df_out[col].fillna(median_crop)

        # 4th level: Global column median if any still remain
        df_out[col] = df_out[col].fillna(df_out[col].median())

    return df_out


def preprocess_raw_data(raw_path: Path = RAW_DATA_PATH, save_path: Optional[Path] = CLEANED_DATA_PATH) -> pd.DataFrame:
    """Run full data cleaning pipeline and optionally save the processed CSV.

    Args:
        raw_path: Path to researchData.xlsx.
        save_path: Path to output cleaned CSV.

    Returns:
        Cleaned pd.DataFrame.
    """
    from ml_pipeline.data_ingestion import load_raw_data

    logger.info("Executing raw data preprocessing pipeline...")
    df = load_raw_data(raw_path)

    # 1. Filter aggregate summary rows
    df = filter_aggregate_rows(df)

    # 2. Clean numeric strings
    df["Extent"] = df["Extent"].apply(clean_numeric_string)
    df["Production"] = df["Production"].apply(clean_numeric_string)

    # 3. Clean Year
    df["Year"] = df["Year"].apply(clean_year_string)
    df = df.dropna(subset=["Year"]).copy()
    df["Year"] = df["Year"].astype(int)

    # 4. Standardize text casing and strip whitespace
    df["District"] = df["District"].astype(str).str.strip()
    # Normalize spelling variations (e.g., 'Monaragala' vs 'Moneragala', 'Hanbantota' vs 'Hambantota')
    district_corrections = {
        "Monaragala": "Moneragala",
        "Hanbantota": "Hambantota",
        "Kaluthara": "Kalutara"
    }
    df["District"] = df["District"].replace(district_corrections)

    df["Season"] = df["Season"].astype(str).str.strip().str.capitalize()
    df["CropCategory"] = df["CropCategory"].astype(str).str.strip()
    df["Crop"] = df["Crop"].astype(str).str.strip()

    # Normalize Crop naming (e.g., 'Chillies (Green)' -> 'Chili')
    crop_corrections = {
        "Chillies (Green)": "Chili",
        "Sweet Potatoes": "Sweet Potato",
        "Potatoes": "Potato",
        "Manioc": "Cassava"
    }
    df["Crop"] = df["Crop"].replace(crop_corrections)

    # 5. Handle anomalies and impute missing values
    df = handle_anomalies_and_impute(df)

    if save_path:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(save_path, index=False)
        logger.info(f"Cleaned dataset saved successfully to {save_path} ({len(df):,} records).")

    return df


if __name__ == "__main__":
    df_cleaned = preprocess_raw_data()
    print("\n--- Cleaned Data Sample ---")
    print(df_cleaned.head())
    print("\nCleaned summary:")
    print(f"Total Rows: {len(df_cleaned):,}")
    print(f"Districts ({df_cleaned['District'].nunique()}): {sorted(df_cleaned['District'].unique())}")
    print(f"Crops ({df_cleaned['Crop'].nunique()})")
    print(f"Years: {df_cleaned['Year'].min()} - {df_cleaned['Year'].max()}")

