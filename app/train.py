#!/usr/bin/env python3
"""
Script d'entrenament (Sessió 7)

Training pipeline complet:
- Versioning automàtic (model_v1.pkl, model_v2.pkl, ...)
- Avaluació amb validation set del pipeline
- Quality gate: deployment_criteria.yaml
- Metadades JSON amb flag deployment_ready
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
import yaml

from app.config import setup_logging

NUMERIC_FEATURES = [
    'Age',
    'Academic Pressure',
    'Work Pressure',
    'CGPA',
    'Study Satisfaction',
    'Job Satisfaction',
    'Work/Study Hours',
    'Financial Stress',
]

CATEGORICAL_FEATURES = [
    'Gender',
    'Sleep Duration',
    'Dietary Habits',
    'Degree',
    'Have you ever had suicidal thoughts ?',
    'Family History of Mental Illness',
]

FEATURE_NAMES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET = 'Depression'

DEFAULT_TRAIN_DATA = 'data/training_set.parquet'
DEFAULT_VAL_DATA = 'data/validation_set.parquet'
DEFAULT_CRITERIA_FILE = 'config/deployment_criteria.yaml'
DEFAULT_MODEL_DIR = 'models'
RANDOM_SEED = 42


def get_next_version(model_dir: str = DEFAULT_MODEL_DIR) -> str:
    """
    Retorna la propera versió disponible (v1, v2, v3, ...).

    Escaneja models/ per trobar model_v*.pkl existents i incrementa.
    """
    models_dir = Path(model_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    existing = []
    for f in models_dir.glob("model_v*.pkl"):
        try:
            existing.append(int(f.stem.split("_v")[1]))
        except (ValueError, IndexError):
            continue

    return f"v{max(existing, default=0) + 1}"


def load_training_data(train_path: str, val_path: str) -> tuple:
    """
    Carrega training i validation splits del pipeline.

    Returns:
        tuple: (X_train, y_train, X_val, y_val)
    """
    logger = logging.getLogger(__name__)

    for path in [train_path, val_path]:
        if not Path(path).exists():
            raise FileNotFoundError(
                f"No s'ha trobat {path}. "
                "Executa primer: python -m app.pipeline"
            )

    train_df = pd.read_parquet(train_path)
    val_df = pd.read_parquet(val_path)

    X_train = train_df[FEATURE_NAMES]
    y_train = train_df[TARGET].astype(int)
    X_val = val_df[FEATURE_NAMES]
    y_val = val_df[TARGET].astype(int)

    logger.info(f"Training:   {len(X_train)} mostres")
    logger.info(f"Validation: {len(X_val)} mostres")

    return X_train, y_train, X_val, y_val


def build_preprocessor() -> ColumnTransformer:
    """Construeix el preprocessador: StandardScaler numèric + OrdinalEncoder categòric."""
    return ColumnTransformer(transformers=[
        ('num', StandardScaler(), NUMERIC_FEATURES),
        ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1),
         CATEGORICAL_FEATURES),
    ])


def train_model(X_train, y_train):
    """
    Entrena i retorna model + preprocessador.

    Returns:
        tuple: (model, preprocessor)
    """
    logger = logging.getLogger(__name__)

    preprocessor = build_preprocessor()
    X_train_processed = preprocessor.fit_transform(X_train)

    model = LogisticRegression(max_iter=2000, random_state=RANDOM_SEED)
    model.fit(X_train_processed, y_train)
    logger.info("Model entrenat: LogisticRegression")

    return model, preprocessor


def evaluate_model(model, preprocessor, X_val, y_val) -> dict:
    """
    Avalua el model sobre el validation set.

    Returns:
        dict amb accuracy, precision, recall, f1_score, roc_auc, confusion_matrix
    """
    logger = logging.getLogger(__name__)

    X_val_processed = preprocessor.transform(X_val)
    y_pred = model.predict(X_val_processed)
    y_prob = model.predict_proba(X_val_processed)[:, 1]

    metrics = {
        'accuracy':  accuracy_score(y_val, y_pred),
        'precision': precision_score(y_val, y_pred, zero_division=0),
        'recall':    recall_score(y_val, y_pred, zero_division=0),
        'f1_score':  f1_score(y_val, y_pred, zero_division=0),
        'roc_auc':   roc_auc_score(y_val, y_prob),
    }

    tn, fp, fn, tp = confusion_matrix(y_val, y_pred).ravel()
    metrics['confusion_matrix'] = {
        'true_negative': int(tn), 'false_positive': int(fp),
        'false_negative': int(fn), 'true_positive': int(tp),
    }

    logger.info(f"Accuracy:  {metrics['accuracy']:.4f}")
    logger.info(f"Precision: {metrics['precision']:.4f}")
    logger.info(f"Recall:    {metrics['recall']:.4f}")
    logger.info(f"F1 Score:  {metrics['f1_score']:.4f}")
    logger.info(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
    logger.info(f"Confusion: TN={tn} FP={fp} FN={fn} TP={tp}")

    return metrics


def check_deployment_criteria(metrics: dict, criteria: dict) -> tuple[bool, list]:
    """
    Comprova si el model compleix els criteris de desplegament.

    Returns:
        tuple: (deployment_ready, failed_checks)
    """
    logger = logging.getLogger(__name__)
    failed = []

    for name, threshold in criteria.items():
        if name.startswith('min_'):
            metric_key = name[4:]  # "min_precision" -> "precision"
            if metric_key in metrics and metrics[metric_key] < threshold:
                failed.append(f"{metric_key} {metrics[metric_key]:.4f} < mínim {threshold}")
        elif name.startswith('max_'):
            metric_key = name[4:]
            if metric_key in metrics and metrics[metric_key] > threshold:
                failed.append(f"{metric_key} {metrics[metric_key]:.4f} > màxim {threshold}")

    is_ready = len(failed) == 0

    if is_ready:
        logger.info("✓ Model compleix tots els criteris de desplegament")
    else:
        logger.warning("✗ Model NO compleix els criteris de desplegament:")
        for f in failed:
            logger.warning(f"  - {f}")

    return is_ready, failed


def save_model_and_metadata(model, preprocessor, metrics: dict, version: str,
                             is_ready: bool, model_dir: str = DEFAULT_MODEL_DIR) -> None:
    """Guarda model (.pkl) i metadades (.json) amb el flag deployment_ready."""
    logger = logging.getLogger(__name__)
    out = Path(model_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Guardar artifacts (model + preprocessor + feature_names)
    model_file = out / f"model_{version}.pkl"
    artifacts = {
        'model': model,
        'preprocessor': preprocessor,
        'feature_names': FEATURE_NAMES,
    }
    joblib.dump(artifacts, model_file)
    logger.info(f"Model guardat: {model_file}")

    # Guardar metadades JSON
    metadata = {
        'version': version,
        'timestamp': datetime.now().isoformat(),
        'model_type': 'logistic_regression',
        'metrics': {k: float(v) if isinstance(v, float) else v
                    for k, v in metrics.items()},
        'deployment_ready': is_ready,
    }

    metadata_file = out / f"metadata_{version}.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Metadades guardades: {metadata_file}")


def run_training(train_data: str, val_data: str,
                 criteria_file: str, model_dir: str) -> None:
    """Executa el training pipeline complet."""
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("INICIANT ENTRENAMENT")
    logger.info("=" * 60)

    version = get_next_version(model_dir)
    logger.info(f"\n[1/4] Versió: {version}")

    logger.info("\n[2/4] Carregant dades...")
    X_train, y_train, X_val, y_val = load_training_data(train_data, val_data)

    logger.info("\n[3/4] Entrenant i avaluant...")
    model, preprocessor = train_model(X_train, y_train)
    metrics = evaluate_model(model, preprocessor, X_val, y_val)

    logger.info("\n[4/4] Quality gate i guardat...")
    with open(criteria_file) as f:
        criteria = yaml.safe_load(f).get('deployment_criteria', {})
    is_ready, _ = check_deployment_criteria(metrics, criteria)
    save_model_and_metadata(model, preprocessor, metrics, version, is_ready, model_dir)

    logger.info("\n" + "=" * 60)
    logger.info(f"ENTRENAMENT COMPLETAT — versió={version}, "
                f"f1={metrics['f1_score']:.4f}, deployment_ready={is_ready}")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Entrenament del model Student Depression (auto-versioning)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--train-data',    default=DEFAULT_TRAIN_DATA)
    parser.add_argument('--val-data',      default=DEFAULT_VAL_DATA)
    parser.add_argument('--criteria-file', default=DEFAULT_CRITERIA_FILE)
    parser.add_argument('--model-dir',     default=DEFAULT_MODEL_DIR)
    parser.add_argument('--log-file',      default='logs/train.log')

    args = parser.parse_args()
    setup_logging(args.log_file)
    run_training(args.train_data, args.val_data, args.criteria_file, args.model_dir)


if __name__ == '__main__':
    main()
