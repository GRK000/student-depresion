#!/usr/bin/env python3
"""
Script d'entrenament (Sessió 5)

Entrena un model de Logistic Regression amb el training split del pipeline
i guarda el model + preprocessador serialitzats.

Exemple d'ús:
    python -m app.pipeline   # Primer generar els splits
    python -m app.train      # Llavors entrenar
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
import joblib
from pathlib import Path


OUTPUT_PATH = 'models/model_v1.pkl'
TRAINING_SET_PATH = 'data/training_set.parquet'
VALIDATION_SET_PATH = 'data/validation_set.parquet'

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


def load_training_data() -> tuple:
    """
    Carrega el training split preparat pel pipeline.

    Returns:
        tuple: (X, y) llests per a model.fit()
    """
    if not Path(TRAINING_SET_PATH).exists():
        raise FileNotFoundError(
            f"No s'ha trobat {TRAINING_SET_PATH}. "
            "Executa primer: python -m app.pipeline"
        )

    df = pd.read_parquet(TRAINING_SET_PATH)
    print(f"  Training set carregat: {len(df)} files")

    X = df[FEATURE_NAMES]
    y = df[TARGET].astype(int)

    return X, y


def train_and_save(output_path: str = OUTPUT_PATH):
    """
    Entrena el model i guarda els artifacts (model + preprocessador).
    """
    print("=" * 60)
    print("TRAINING MODEL - Session 5")
    print("=" * 60)

    # [1/4] Carregar training split del pipeline
    print("\n[1/4] Loading training data from pipeline split...")
    X, y = load_training_data()
    print(f"  Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"  Target distribution: {y.value_counts().to_dict()}")

    # [2/4] Split train/test intern
    print("\n[2/4] Splitting train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train)} samples")
    print(f"  Test:  {len(X_test)} samples")

    # [3/4] Preprocessador + entrenament
    print("\n[3/4] Training model...")
    preprocessor = ColumnTransformer(transformers=[
        ('num', StandardScaler(), NUMERIC_FEATURES),
        ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1),
         CATEGORICAL_FEATURES),
    ])

    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    model = LogisticRegression(max_iter=2000, random_state=42)
    model.fit(X_train_processed, y_train)

    accuracy = model.score(X_test_processed, y_test)
    print(f"  Test accuracy: {accuracy:.2%}")

    # [4/4] Guardar artifacts
    print("\n[4/4] Saving model...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    artifacts = {
        'model': model,
        'preprocessor': preprocessor,
        'feature_names': FEATURE_NAMES,
    }
    joblib.dump(artifacts, output_path)
    print(f"  ✓ Model saved to: {output_path}")

    print("\n" + "=" * 60)
    print("TRAINING COMPLETED")
    print("=" * 60)


if __name__ == '__main__':
    train_and_save()
