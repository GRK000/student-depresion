#!/usr/bin/env python3
"""
Script d'entrenament (Sessió 2)

Entrena un model de Logistic Regression amb el dataset Student Depression
i guarda el model + preprocessador serialitzats.

Exemple d'ús:
    python -m app.train
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
import joblib
from pathlib import Path


DATA_PATH = 'data/raw/student_depression_dataset.csv'
OUTPUT_PATH = 'models/model_v1.pkl'

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


def load_and_preprocess(data_path: str) -> tuple:
    """
    Carrega i preprocessa el dataset Student Depression.

    Returns:
        tuple: (X, y) amb features i target
    """
    df = pd.read_csv(data_path)
    print(f"  Loaded {len(df)} rows")

    # Seleccionar features i target
    df = df[FEATURE_NAMES + [TARGET]].copy()

    # Financial Stress pot contenir '?' — convertir a NaN
    df['Financial Stress'] = pd.to_numeric(df['Financial Stress'], errors='coerce')

    # Eliminar files amb NaN
    before = len(df)
    df.dropna(inplace=True)
    dropped = before - len(df)
    if dropped > 0:
        print(f"  Eliminades {dropped} files amb valors nuls")

    X = df[FEATURE_NAMES]
    y = df[TARGET].astype(int)

    return X, y


def train_and_save(data_path: str = DATA_PATH, output_path: str = OUTPUT_PATH):
    """
    Entrena el model i guarda els artifacts (model + preprocessador).
    """
    print("=" * 60)
    print("TRAINING MODEL - Session 2")
    print("=" * 60)

    # [1/4] Carregar i preprocessar dades
    print("\n[1/4] Loading and preprocessing data...")
    X, y = load_and_preprocess(data_path)
    print(f"  Dataset: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"  Target distribution: {y.value_counts().to_dict()}")

    # [2/4] Split train/test
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
