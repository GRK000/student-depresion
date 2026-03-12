"""API endpoint tests (Session 11) — 6 tests."""
import json


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
    incomplete = {"age": 22, "gender": "Female"}  # Falten camps obligatoris
    response = client.post("/predict", json=incomplete)
    assert response.status_code == 422


def test_predict_invalid_range(client, valid_student_data):
    """POST /predict with out-of-range age returns 422."""
    bad_data = valid_student_data.copy()
    bad_data["age"] = 150  # > 60, fora del rang vàlid
    response = client.post("/predict", json=bad_data)
    assert response.status_code == 422


def test_predict_returns_model_version(client, valid_student_data, temp_predictions_log):
    """POST /predict response includes a non-empty model_version."""
    response = client.post("/predict", json=valid_student_data)
    assert response.status_code == 200
    assert response.json()["model_version"]  # string no buit


def test_predict_logs_to_file(client, valid_student_data, temp_predictions_log):
    """POST /predict logs prediction to JSON Lines file.

    Test d'integració: travessa HTTP → model → sistema de fitxers.
    Verifica un efecte secundari real, no només la resposta de l'API.
    """
    response = client.post("/predict", json=valid_student_data)
    assert response.status_code == 200

    assert temp_predictions_log.exists()

    with temp_predictions_log.open("r") as f:
        logs = [json.loads(line.strip()) for line in f if line.strip()]

    assert len(logs) >= 1
    latest = logs[-1]
    assert latest["prediction"] in [0, 1]
    assert "timestamp" in latest
    assert "model_version" in latest
    assert "probability" in latest
    assert latest["input"]["Age"] == valid_student_data["age"]
