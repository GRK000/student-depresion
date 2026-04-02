"""API endpoint tests."""

import json


def test_root_serves_frontend(client):
    """GET / serves the built SPA entrypoint when available."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Wellbeing Compass" in response.text


def test_health_endpoint(client):
    """GET /health returns 200 with healthy status."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "model_version" in data


def test_predict_valid_input(client, valid_student_data, temp_predictions_log):
    """POST /predict with valid data returns 200 with prediction."""
    response = client.post("/predict", json=valid_student_data)
    assert response.status_code == 200

    data = response.json()
    assert data["prediction"] in [0, 1]
    assert 0.0 <= data["probability"] <= 1.0
    assert "model_version" in data


def test_predict_missing_field(client):
    """POST /predict with missing fields returns 422."""
    incomplete = {"age": 22, "gender": "Female"}
    response = client.post("/predict", json=incomplete)
    assert response.status_code == 422


def test_predict_invalid_range(client, valid_student_data):
    """POST /predict with out-of-range age returns 422."""
    bad_data = valid_student_data.copy()
    bad_data["age"] = 150
    response = client.post("/predict", json=bad_data)
    assert response.status_code == 422


def test_predict_returns_model_version(client, valid_student_data, temp_predictions_log):
    """POST /predict response includes a non-empty model_version."""
    response = client.post("/predict", json=valid_student_data)
    assert response.status_code == 200
    assert response.json()["model_version"]


def test_predict_logs_to_file(client, valid_student_data, temp_predictions_log):
    """POST /predict logs prediction to JSON Lines file."""
    response = client.post("/predict", json=valid_student_data)
    assert response.status_code == 200

    assert temp_predictions_log.exists()

    with temp_predictions_log.open("r", encoding="utf-8") as file_handle:
        logs = [json.loads(line.strip()) for line in file_handle if line.strip()]

    assert len(logs) >= 1
    latest = logs[-1]
    assert latest["prediction"] in [0, 1]
    assert "timestamp" in latest
    assert "model_version" in latest
    assert "probability" in latest
    assert latest["input"]["Age"] == valid_student_data["age"]


def test_client_side_route_falls_back_to_frontend(client):
    """Unknown client-side routes should fall back to index.html."""
    response = client.get("/results")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Wellbeing Compass" in response.text
