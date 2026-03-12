"""Shared test fixtures (Session 11)."""
import pytest
import joblib
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient
from app.api import app
from app.config import settings

MODEL_PATH = settings.resolve_path(settings.MODEL_PATH)


@pytest.fixture(scope="session")
def client():
    """FastAPI test client with model loaded via lifespan startup."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def temp_predictions_log(tmp_path, monkeypatch):
    """Redirect predictions log to a temp file for every test.

    Using autouse=True ensures no test writes to the real predictions file,
    even tests that don't explicitly assert on log contents.
    """
    log_file = tmp_path / "predictions.jsonl"
    monkeypatch.setattr("app.pred_store.settings.PREDICTIONS_LOG_PATH", str(log_file))
    return log_file


@pytest.fixture(scope="session")
def loaded_model():
    """Load model once for the entire test session."""
    return joblib.load(MODEL_PATH)


@pytest.fixture
def valid_student_data():
    """Valid prediction request data matching StudentDepressionInput schema."""
    return {
        "age": 28.0,
        "academic_pressure": 3.0,
        "work_pressure": 0.0,
        "cgpa": 7.03,
        "study_satisfaction": 5.0,
        "job_satisfaction": 0.0,
        "work_study_hours": 9.0,
        "financial_stress": 1.0,
        "gender": "Male",
        "sleep_duration": "Less than 5 hours",
        "dietary_habits": "Healthy",
        "degree": "BA",
        "suicidal_thoughts": "No",
        "family_history": "Yes",
    }


@pytest.fixture
def sample_dataframe():
    """Small DataFrame for testing pipeline functions."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "City": ["CityA", "CityB", "CityC", "CityD", "CityE"],
        "Profession": ["Student", "Student", "Student", "Student", "Student"],
        "Gender": ["Male", "Female", "Male", "Female", "Male"],
        "Age": [22, 25, 21, 28, 23],
        "Academic Pressure": [4, 3, 5, 2, 3],
        "Work Pressure": [2, 1, 0, 3, 2],
        "CGPA": [7.5, 8.0, 6.5, 7.0, 8.5],
        "Study Satisfaction": [3, 4, 2, 5, 3],
        "Job Satisfaction": [2, 3, 1, 4, 2],
        "Sleep Duration": [
            "5-6 hours", "7-8 hours", "Less than 5 hours",
            "More than 8 hours", "5-6 hours",
        ],
        "Dietary Habits": ["Healthy", "Moderate", "Unhealthy", "Healthy", "Moderate"],
        "Degree": ["BSc", "B.Tech", "BA", "MBA", "BSc"],
        "Have you ever had suicidal thoughts ?": ["No", "Yes", "No", "No", "Yes"],
        "Work/Study Hours": [8, 6, 10, 4, 7],
        "Financial Stress": [3, 2, 5, 1, 4],
        "Family History of Mental Illness": ["No", "Yes", "No", "Yes", "No"],
        "Depression": [1, 0, 1, 0, 1],
    })
