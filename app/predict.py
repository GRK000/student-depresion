#!/usr/bin/env python3
"""
Script de predicció per línia de comandes (Sessió 1)

Exemple d'ús:
    python -m app.predict --model models/model_v0.1.0.pkl \
        --input '{"Age": 24, "Gender": "Female", "Academic Pressure": 4.0, "Work Pressure": 0.0, "CGPA": 6.5, "Study Satisfaction": 2.0, "Job Satisfaction": 0.0, "Sleep Duration": "5-6 hours", "Dietary Habits": "Moderate", "Degree": "BSc", "Have you ever had suicidal thoughts ?": "Yes", "Work/Study Hours": 8.0, "Financial Stress": 4.0, "Family History of Mental Illness": "No"}'
"""

import argparse
import json
import joblib
import pandas as pd


# Features numèriques i categòriques del dataset Student Depression
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

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_model(model_path: str):
    """Carrega el model i preprocessador serialitzats."""
    artifacts = joblib.load(model_path)
    return artifacts['model'], artifacts['preprocessor'], artifacts['feature_names']


def make_prediction(model, preprocessor, feature_names: list, patient_data: dict):
    """Fa una predicció amb el model (aplicant preprocessament)."""
    X = pd.DataFrame([patient_data], columns=feature_names)
    X_processed = preprocessor.transform(X)
    prediction = model.predict(X_processed)[0]

    if hasattr(model, 'predict_proba'):
        probability = model.predict_proba(X_processed)[0]
        return prediction, probability

    return prediction, None


def main():
    parser = argparse.ArgumentParser(description='Fer predicció de depressió en estudiants')

    parser.add_argument('--model', type=str, required=True,
                        help='Path al model serialitzat (.pkl)')
    parser.add_argument('--input', type=str, required=True,
                        help='Dades de l\'estudiant en format JSON')

    args = parser.parse_args()

    # Carregar model i preprocessador
    print(f"Carregant model des de {args.model}...")
    model, preprocessor, feature_names = load_model(args.model)

    # Parsejar el JSON d'entrada
    try:
        patient_data = json.loads(args.input)
    except json.JSONDecodeError as e:
        print(f"Error: El JSON no és vàlid - {e}")
        return

    # Comprovar que hi ha totes les features
    missing = [f for f in feature_names if f not in patient_data]
    if missing:
        print(f"Error: Falten els camps {missing} al JSON")
        return

    # Filtrar només les features esperades (en ordre)
    input_data = {f: patient_data[f] for f in feature_names}

    # Fer predicció
    prediction, probability = make_prediction(model, preprocessor, feature_names, input_data)

    # Mostrar resultat
    print("\n" + "=" * 50)
    print("RESULTAT DE LA PREDICCIÓ")
    print("=" * 50)
    print(f"Predicció: {prediction}")

    if probability is not None:
        print(f"Probabilitat sense depressió (0): {probability[0]:.2%}")
        print(f"Probabilitat amb depressió    (1): {probability[1]:.2%}")

    if prediction == 1:
        print("\n⚠️  Risc de depressió detectat")
    else:
        print("\n✓ No s'ha detectat risc de depressió")
    print("=" * 50)


if __name__ == "__main__":
    main()
