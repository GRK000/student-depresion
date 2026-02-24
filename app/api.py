"""
API d'inferència per a predicció de depressió en estudiants (Sessió 2)

Endpoints:
    GET  /health  - Health check
    POST /predict - Fer predicció
"""

from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from typing import Optional
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer


# Variables globals per emmagatzemar el model i preprocessador (carregats a l'inici)
_model: Optional[LogisticRegression] = None
_preprocessor: Optional[ColumnTransformer] = None
_feature_names: Optional[list] = None
_model_version = "v1"

FEATURE_NAMES = [
    'Age', 'Academic Pressure', 'Work Pressure', 'CGPA',
    'Study Satisfaction', 'Job Satisfaction', 'Work/Study Hours', 'Financial Stress',
    'Gender', 'Sleep Duration', 'Dietary Habits', 'Degree',
    'Have you ever had suicidal thoughts ?', 'Family History of Mental Illness',
]


def load_model():
    """Carregar el model i preprocessador a l'inici de l'aplicació."""
    global _model, _preprocessor, _feature_names
    print("Carregant model...")
    artifacts = joblib.load("models/model_v1.pkl")
    _model = artifacts['model']
    _preprocessor = artifacts['preprocessor']
    _feature_names = artifacts['feature_names']
    print(f"Model carregat: {type(_model).__name__}")


# Lifespan context manager (modern FastAPI pattern)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestió del cicle de vida de l'aplicació (startup/shutdown)."""
    load_model()
    yield
    print("Shutting down...")


app = FastAPI(
    title="Student Depression Prediction API",
    version="1.0.0",
    description="API per predir risc de depressió en estudiants",
    lifespan=lifespan,
)

# 🔮 NOTA PER SESSIONS FUTURES:
# Sessió 3: Afegirem validació amb Pydantic (BaseModel, Field)
# Sessió 4: El path del model es llegirà des d'un fitxer .env + logging professional


# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    """Endpoint arrel amb informació bàsica."""
    return {
        "message": "Student Depression Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health_check():
    """Health check: retorna l'estat del servei i el model carregat."""
    return {
        "status": "healthy",
        "model_loaded": _model is not None,
        "model_version": _model_version,
    }


@app.post("/predict")
async def predict(request: Request):
    """
    Predicció de depressió per a un estudiant.

    Esperem un JSON amb:
        Age, Academic Pressure, Work Pressure, CGPA,
        Study Satisfaction, Job Satisfaction, Work/Study Hours, Financial Stress,
        Gender, Sleep Duration, Dietary Habits, Degree,
        Have you ever had suicidal thoughts ?, Family History of Mental Illness
    """
    if _model is None or _preprocessor is None or _feature_names is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    data = await request.json()

    # Comprovar camps (sense Pydantic per ara — Sessió 3 ho farà automàticament)
    missing = [f for f in _feature_names if f not in data]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing fields: {missing}")

    # Construir DataFrame en l'ordre esperat
    X = pd.DataFrame([{f: data[f] for f in _feature_names}])

    # Preprocessar i predir
    X_processed = _preprocessor.transform(X)
    prediction = int(_model.predict(X_processed)[0])

    probability = None
    if hasattr(_model, 'predict_proba'):
        proba = _model.predict_proba(X_processed)[0]
        probability = float(proba[1])

    return {
        "prediction": prediction,
        "probability": probability,
        "model_version": _model_version,
    }
