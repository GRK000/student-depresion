"""Pipeline and schema tests (Session 11) — 4 tests."""
import pytest
import pandas as pd
from pydantic import ValidationError

from app.pipeline import normalize_columns
from app.schemas import StudentDepressionInput


def test_normalize_columns_drops_metadata(sample_dataframe):
    """normalize_columns drops id, City, and Profession columns."""
    result = normalize_columns(sample_dataframe)
    assert "id" not in result.columns
    assert "City" not in result.columns
    assert "Profession" not in result.columns


def test_normalize_columns_keeps_features(sample_dataframe):
    """normalize_columns keeps all 14 feature columns + Depression target."""
    result = normalize_columns(sample_dataframe)
    expected_features = [
        "Gender", "Age", "Academic Pressure", "Work Pressure", "CGPA",
        "Study Satisfaction", "Job Satisfaction", "Sleep Duration",
        "Dietary Habits", "Degree", "Have you ever had suicidal thoughts ?",
        "Work/Study Hours", "Financial Stress",
        "Family History of Mental Illness", "Depression",
    ]
    for col in expected_features:
        assert col in result.columns, f"Missing column: {col}"


def test_schema_validation_valid(valid_student_data):
    """StudentDepressionInput accepts valid input without error."""
    model = StudentDepressionInput(**valid_student_data)
    assert model.age == valid_student_data["age"]
    assert model.gender == valid_student_data["gender"]


def test_schema_validation_invalid_age(valid_student_data):
    """StudentDepressionInput rejects out-of-range age (>60) with ValidationError."""
    bad_data = valid_student_data.copy()
    bad_data["age"] = 150  # > 60, fora del rang vàlid (ge=18, le=60)
    with pytest.raises(ValidationError):
        StudentDepressionInput(**bad_data)
