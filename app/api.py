"""
API d'inferència per a predicció de depressió en estudiants (Sessió 2)

Endpoints:
    GET  /health  - Health check
    POST /predict - Fer predicció
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from typing import Optional
import logging
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer

from app.schemas import StudentDepressionInput, PredictionResponse, HealthResponse
from app.config import settings, setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


# Variables globals per emmagatzemar el model i preprocessador (carregats a l'inici)
_model: Optional[LogisticRegression] = None
_preprocessor: Optional[ColumnTransformer] = None
_feature_names: Optional[list] = None
_model_version = None

FEATURE_NAMES = [
    'Age', 'Academic Pressure', 'Work Pressure', 'CGPA',
    'Study Satisfaction', 'Job Satisfaction', 'Work/Study Hours', 'Financial Stress',
    'Gender', 'Sleep Duration', 'Dietary Habits', 'Degree',
    'Have you ever had suicidal thoughts ?', 'Family History of Mental Illness',
]


def load_model():
    """Carregar el model i preprocessador a l'inici de l'aplicació."""
    global _model, _preprocessor, _feature_names, _model_version
    model_path = settings.resolve_path(settings.MODEL_PATH)
    logger.info(f"Carregant model des de {model_path}...")
    artifacts = joblib.load(str(model_path))
    _model = artifacts['model']
    _preprocessor = artifacts['preprocessor']
    _feature_names = artifacts['feature_names']
    _model_version = settings.APP_VERSION
    logger.info(f"Model carregat: {type(_model).__name__}")


# Lifespan context manager (modern FastAPI pattern)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestió del cicle de vida de l'aplicació (startup/shutdown)."""
    load_model()
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API per predir risc de depressió en estudiants",
    lifespan=lifespan,
)


# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    """Endpoint arrel amb informació bàsica."""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "docs": "/docs",
        },
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check: retorna l'estat del servei i el model carregat."""
    return {
        "status": "healthy",
        "model_loaded": _model is not None,
        "model_version": _model_version,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: StudentDepressionInput):
    """
    Predicció de depressió per a un estudiant.

    Accepta un JSON validat per Pydantic amb les 14 features del dataset.
    Retorna la predicció (0/1), la probabilitat i la versió del model.
    """
    if _model is None or _preprocessor is None or _feature_names is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Les dades ja estan validades per Pydantic!
    features_dict = request.to_model_dict()

    # Construir DataFrame en l'ordre esperat
    X = pd.DataFrame([features_dict])[_feature_names]

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


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    """
    Custom handler per errors de validació de Pydantic.

    Retorna missatges d'error més clars quan les dades d'entrada són invàlides.
    """
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "detail": str(exc)
        }
    )
