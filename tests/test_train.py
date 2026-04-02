"""Unit tests for the training comparison workflow."""

import pandas as pd

from app.train import (
    build_error_narrative,
    select_best_candidate,
    summarize_categorical_deltas,
    summarize_numeric_deltas,
)


def test_select_best_candidate_prioritizes_recall_among_ready_models():
    results = [
        {
            "name": "High Precision",
            "model_type": "logistic_regression",
            "deployment_ready": True,
            "failed_checks": [],
            "metrics": {
                "recall": 0.81,
                "precision": 0.92,
                "f1_score": 0.86,
                "roc_auc": 0.90,
                "accuracy": 0.88,
            },
        },
        {
            "name": "High Recall",
            "model_type": "xgboost",
            "deployment_ready": True,
            "failed_checks": [],
            "metrics": {
                "recall": 0.89,
                "precision": 0.84,
                "f1_score": 0.86,
                "roc_auc": 0.89,
                "accuracy": 0.86,
            },
        },
    ]

    winner, ranked = select_best_candidate(results)

    assert winner["name"] == "High Recall"
    assert ranked[0]["selected"] is True
    assert ranked[0]["selection_rank"] == 1
    assert ranked[1]["selection_rank"] == 2


def test_select_best_candidate_prefers_ready_models_before_metrics():
    results = [
        {
            "name": "Not Ready",
            "model_type": "random_forest",
            "deployment_ready": False,
            "failed_checks": ["precision 0.71 < minimum 0.75"],
            "metrics": {
                "recall": 0.95,
                "precision": 0.71,
                "f1_score": 0.81,
                "roc_auc": 0.89,
                "accuracy": 0.79,
            },
        },
        {
            "name": "Ready",
            "model_type": "logistic_regression",
            "deployment_ready": True,
            "failed_checks": [],
            "metrics": {
                "recall": 0.88,
                "precision": 0.84,
                "f1_score": 0.86,
                "roc_auc": 0.90,
                "accuracy": 0.85,
            },
        },
    ]

    winner, _ = select_best_candidate(results)
    assert winner["name"] == "Ready"


def test_summarize_numeric_deltas_sorts_by_absolute_difference():
    group_df = pd.DataFrame(
        {
            "Age": [30, 32],
            "Academic Pressure": [5, 5],
            "Work Pressure": [1, 1],
            "CGPA": [6.0, 6.2],
            "Study Satisfaction": [1, 1],
            "Job Satisfaction": [1, 1],
            "Work/Study Hours": [11, 10],
            "Financial Stress": [5, 4],
        }
    )
    reference_df = pd.DataFrame(
        {
            "Age": [24, 25],
            "Academic Pressure": [2, 2],
            "Work Pressure": [1, 1],
            "CGPA": [7.5, 7.7],
            "Study Satisfaction": [4, 4],
            "Job Satisfaction": [2, 2],
            "Work/Study Hours": [7, 6],
            "Financial Stress": [2, 2],
        }
    )

    summary = summarize_numeric_deltas(group_df, reference_df, top_n=2)

    assert len(summary) == 2
    assert summary[0]["feature"] == "Age"
    assert summary[1]["feature"] in {"Work/Study Hours", "Academic Pressure"}


def test_summarize_categorical_deltas_returns_overrepresented_categories():
    group_df = pd.DataFrame(
        {
            "Gender": ["Female", "Female", "Male"],
            "Sleep Duration": ["Less than 5 hours", "Less than 5 hours", "5-6 hours"],
            "Dietary Habits": ["Unhealthy", "Unhealthy", "Moderate"],
            "Degree": ["BSc", "BSc", "BA"],
            "Have you ever had suicidal thoughts ?": ["Yes", "Yes", "No"],
            "Family History of Mental Illness": ["Yes", "No", "Yes"],
        }
    )
    reference_df = pd.DataFrame(
        {
            "Gender": ["Male", "Male", "Female"],
            "Sleep Duration": ["7-8 hours", "5-6 hours", "7-8 hours"],
            "Dietary Habits": ["Healthy", "Moderate", "Healthy"],
            "Degree": ["BSc", "MBA", "MBA"],
            "Have you ever had suicidal thoughts ?": ["No", "No", "No"],
            "Family History of Mental Illness": ["No", "No", "No"],
        }
    )

    summary = summarize_categorical_deltas(group_df, reference_df, top_n=3)

    assert len(summary) == 3
    assert all(row["delta"] > 0 for row in summary)
    assert any(row["feature"] == "Have you ever had suicidal thoughts ?" for row in summary)


def test_build_error_narrative_uses_numeric_and_categorical_signals():
    narrative = build_error_narrative(
        "False negatives",
        numeric_signals=[
            {"feature": "Academic Pressure", "delta": 1.2},
            {"feature": "Work/Study Hours", "delta": -0.8},
        ],
        categorical_signals=[
            {"feature": "Sleep Duration", "category": "Less than 5 hours"},
        ],
    )

    assert "higher Academic Pressure" in narrative
    assert "lower Work/Study Hours" in narrative
    assert "Sleep Duration=Less than 5 hours" in narrative
