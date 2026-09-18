"""Data Ingestion Module for CropForecastLK.

Responsible for loading and auditing the raw census agricultural records
from the Department of Census and Statistics, Sri Lanka.
"""
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
from ml_pipeline.config import RAW_DATA_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "District",
    "Season",
    "CropCategory",
    "Crop",
    "Year",
    "Extent",
    "Production"
]


def load_raw_data(file_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw agricultural dataset from Excel.

    Args:
        file_path: Path to the researchData.xlsx file.

    Returns:
        pd.DataFrame containing raw agricultural records.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Raw data file not found at: {file_path}")

    logger.info(f"Loading raw agricultural dataset from {file_path}...")
    df = pd.read_excel(file_path)
    logger.info(f"Loaded {len(df):,} records across {len(df.columns)} columns.")
    return df


def validate_schema(df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
    """Validate that the loaded DataFrame matches expected schema requirements.

    Args:
        df: Input DataFrame to validate.

    Returns:
        Tuple of (is_valid: bool, audit_report: dict).
    """
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    is_valid = len(missing_cols) == 0

    report = {
        "row_count": len(df),
        "col_count": len(df.columns),
        "columns": df.columns.tolist(),
        "missing_expected_columns": missing_cols,
        "null_counts": df.isna().sum().to_dict(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "is_valid": is_valid
    }

    if not is_valid:
        logger.warning(f"Schema validation failed! Missing columns: {missing_cols}")
    else:
        logger.info("Schema validation passed successfully.")

    return is_valid, report


def get_raw_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate high-level profile of categorical variables and anomalies.

    Args:
        df: Raw DataFrame.

    Returns:
        Dictionary summarizing unique values, top categories, and missingness.
    """
    return {
        "unique_districts": int(df["District"].nunique()),
        "districts_sample": df["District"].dropna().unique().tolist()[:10],
        "seasons": df["Season"].value_counts().to_dict(),
        "categories_count": int(df["CropCategory"].nunique()),
        "unique_crops_count": int(df["Crop"].nunique()),
        "years_count": int(df["Year"].nunique()),
        "raw_missing_extent": int(df["Extent"].isna().sum()),
        "raw_missing_production": int(df["Production"].isna().sum()),
    }


if __name__ == "__main__":
    df_raw = load_raw_data()
    valid, audit = validate_schema(df_raw)
    summary = get_raw_summary(df_raw)
    print("\n--- Raw Data Audit ---")
    print(f"Total Rows: {audit['row_count']}")
    print(f"Validation Status: {'PASSED' if valid else 'FAILED'}")
    print(f"Unique Crops: {summary['unique_crops_count']}")
    print(f"Seasons: {summary['seasons']}")
