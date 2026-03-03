"""Prediction persistence: write and read inference records (JSON Lines)."""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from app.config import settings


def save_prediction(
    input_data: Dict[str, Any],
    prediction: int,
    probability: float,
    model_version: str
) -> None:
    """
    Save a prediction record to the JSON Lines store.

    Args:
        input_data: Input features dictionary
        prediction: Model prediction (0 or 1)
        probability: Prediction probability
        model_version: Version of model used
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input": input_data,
        "prediction": prediction,
        "probability": probability,
        "model_version": model_version
    }

    store_file = Path(settings.PREDICTIONS_LOG_PATH)
    store_file.parent.mkdir(parents=True, exist_ok=True)

    with store_file.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def find_all_predictions(limit: int = 100) -> list[Dict[str, Any]]:
    """
    Return prediction records from the store.

    Args:
        limit: Maximum number of records to return

    Returns:
        List of prediction records (most recent first)
    """
    store_file = Path(settings.PREDICTIONS_LOG_PATH)

    if not store_file.exists():
        return []

    records = []
    with store_file.open("r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line.strip()))

    return records[-limit:][::-1]  # Return most recent first
