from pathlib import Path
from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "CropForecastLK API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Base paths
    BACKEND_DIR: Path = Path(__file__).resolve().parent.parent.parent
    ROOT_DIR: Path = BACKEND_DIR.parent
    
    MODEL_PATH: Path = ROOT_DIR / "data" / "artifacts" / "crop_forecaster_pipeline.joblib"
    METADATA_PATH: Path = ROOT_DIR / "data" / "artifacts" / "model_metadata.json"
    CLEANED_DATA_PATH: Path = ROOT_DIR / "data" / "processed" / "cleaned_highland_crops.csv"
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"
    ]

    model_config = {"case_sensitive": True}


settings = Settings()
