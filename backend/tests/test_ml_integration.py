"""Integration Tests for Serialized Pipeline and Domain Invariants."""
import pytest
from pathlib import Path
import joblib
from ml_pipeline.config import PIPELINE_EXPORT_PATH, HIGHLAND_DISTRICTS, TARGET_CROPS
from ml_pipeline.export_pipeline import CropForecasterPipeline


def test_pipeline_artifact_exists_and_loads():
    assert PIPELINE_EXPORT_PATH.exists(), "Trained pipeline artifact missing!"
    pipeline = joblib.load(PIPELINE_EXPORT_PATH)
    assert isinstance(pipeline, CropForecasterPipeline)


@pytest.mark.parametrize("district", HIGHLAND_DISTRICTS)
def test_all_highland_districts_inference(district: str):
    pipeline: CropForecasterPipeline = joblib.load(PIPELINE_EXPORT_PATH)
    res = pipeline.predict_single(
        district=district,
        season="Maha",
        crop="Potato" if district in ["Nuwara Eliya", "Badulla"] else "Maize",
        extent_ha=200.0,
        year=2024
    )
    assert res["predicted_production_mt"] >= 0.0
    assert res["predicted_yield_mt_per_ha"] >= 0.0
    assert res["district"] == district


@pytest.mark.parametrize("crop", TARGET_CROPS)
def test_all_target_crops_inference(crop: str):
    pipeline: CropForecasterPipeline = joblib.load(PIPELINE_EXPORT_PATH)
    res = pipeline.predict_single(
        district="Badulla",
        season="Yala",
        crop=crop,
        extent_ha=150.0,
        year=2024
    )
    assert res["predicted_production_mt"] >= 0.0
    assert res["crop"] == crop
