"""Model loading tests (Session 11) — 2 tests."""
import pytest
import pandas as pd
from app.config import settings

MODEL_PATH = settings.resolve_path(settings.MODEL_PATH)


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="Model file not found")
def test_model_loads_successfully(loaded_model):
    """Model loads without error and contains expected keys."""
    assert loaded_model is not None
    assert "model" in loaded_model
    assert "preprocessor" in loaded_model
    assert "feature_names" in loaded_model
    assert hasattr(loaded_model["model"], "predict")
    assert hasattr(loaded_model["model"], "predict_proba")


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="Model file not found")
def test_model_prediction_format(loaded_model):
    """Prediction is 0 or 1, probabilities in [0, 1]."""
    model = loaded_model["model"]
    preprocessor = loaded_model["preprocessor"]
    feature_names = loaded_model["feature_names"]

    X = pd.DataFrame([{
        "Age": 28, "Academic Pressure": 3, "Work Pressure": 0,
        "CGPA": 7.03, "Study Satisfaction": 5, "Job Satisfaction": 0,
        "Work/Study Hours": 9, "Financial Stress": 1,
        "Gender": "Male", "Sleep Duration": "Less than 5 hours",
        "Dietary Habits": "Healthy", "Degree": "BA",
        "Have you ever had suicidal thoughts ?": "No",
        "Family History of Mental Illness": "Yes",
    }])[feature_names]

    X_processed = preprocessor.transform(X)
    prediction = model.predict(X_processed)[0]
    assert prediction in [0, 1]

    proba = model.predict_proba(X_processed)[0]
    assert len(proba) == 2
    assert all(0.0 <= p <= 1.0 for p in proba)
