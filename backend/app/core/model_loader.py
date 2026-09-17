"""Singleton Model Loader for In-Memory Low-Latency Inference."""
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import joblib

from backend.app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ModelLoader:
    _instance: Optional["ModelLoader"] = None
    _pipeline: Any = None
    _metadata: Dict[str, Any] = {}

    def __new__(cls) -> "ModelLoader":
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    def load(self, model_path: Path = settings.MODEL_PATH, metadata_path: Path = settings.METADATA_PATH) -> None:
        """Load serialized pipeline and metadata into RAM."""
        if not model_path.exists():
            logger.error(f"Model artifact not found at {model_path}!")
            return

        logger.info(f"Loading ML pipeline from {model_path}...")
        self._pipeline = joblib.load(model_path)

        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                self._metadata = json.load(f)
            logger.info("Model metadata loaded successfully.")
        else:
            self._metadata = {"version": "1.0.0", "model_type": "XGBoost"}

        logger.info("Pipeline loaded into RAM. Ready for inference.")

    @property
    def is_loaded(self) -> bool:
        return self._pipeline is not None

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata

    def predict(
        self,
        district: str,
        season: str,
        crop: str,
        extent_ha: float,
        year: int = 2024
    ) -> Dict[str, Any]:
        """Perform sub-50ms thread-safe in-memory inference."""
        if not self.is_loaded:
            raise RuntimeError("Model pipeline has not been initialized or loaded into RAM.")

        return self._pipeline.predict_single(
            district=district,
            season=season,
            crop=crop,
            extent_ha=extent_ha,
            year=year
        )

    def predict_batch(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform batch inference."""
        if not self.is_loaded:
            raise RuntimeError("Model pipeline has not been initialized or loaded into RAM.")
        return [self.predict(**s) for s in scenarios]


model_loader = ModelLoader()
