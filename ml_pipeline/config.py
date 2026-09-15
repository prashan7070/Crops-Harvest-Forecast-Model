from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "researchData.xlsx"
PROCESSED_DIR = DATA_DIR / "processed"
CLEANED_DATA_PATH = PROCESSED_DIR / "cleaned_highland_crops.csv"
ENGINEERED_FEATURES_PATH = PROCESSED_DIR / "engineered_features.csv"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
PIPELINE_EXPORT_PATH = ARTIFACTS_DIR / "crop_forecaster_pipeline.joblib"
BEST_PARAMS_PATH = ARTIFACTS_DIR / "optuna_study_best_params.json"
MODEL_METADATA_PATH = ARTIFACTS_DIR / "model_metadata.json"

DOCS_DIR = BASE_DIR / "docs"

# Agricultural Domain Definitions
HIGHLAND_DISTRICTS = [
    "Nuwara Eliya",
    "Badulla",
    "Kandy",
    "Matale",
    "Monaragala"
]

TARGET_CROPS = [
    "Kurakkan",
    "Maize",
    "Green Gram",
    "Chillies (Green)",
    "Potatoes",
    "Sweet Potatoes",
    "Manioc"
]

SEASONS = ["Yala", "Maha"]

# Temporal Split Boundaries
TRAIN_MAX_YEAR = 2017
VAL_MAX_YEAR = 2020
TEST_MAX_YEAR = 2023

# Modeling Settings
RANDOM_STATE = 42
CV_FOLDS = 5
OPTUNA_TRIALS = 50
