"""FastAPI inference service and SPA host for the wellbeing assessment app."""

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression

from app.config import settings, setup_logging
from app.pred_store import find_all_predictions, save_prediction
from app.schemas import HealthResponse, PredictionResponse, StudentDepressionInput

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


# Variables globals per emmagatzemar el model i preprocessador (carregats a l'inici)
_model: Optional[LogisticRegression] = None
_preprocessor: Optional[ColumnTransformer] = None
_feature_names: Optional[list] = None
_model_version = None

FEATURE_NAMES = [
    "Age",
    "Academic Pressure",
    "Work Pressure",
    "CGPA",
    "Study Satisfaction",
    "Job Satisfaction",
    "Work/Study Hours",
    "Financial Stress",
    "Gender",
    "Sleep Duration",
    "Dietary Habits",
    "Degree",
    "Have you ever had suicidal thoughts ?",
    "Family History of Mental Illness",
]

FRONTEND_DIR = Path(__file__).parent / "frontend"
FRONTEND_ASSETS_DIR = FRONTEND_DIR / "assets"
FRONTEND_INDEX = FRONTEND_DIR / "index.html"


def load_model():
    """Carregar el model i preprocessador a l'inici de l'aplicació."""
    global _model, _preprocessor, _feature_names, _model_version
    model_path = settings.resolve_path(settings.MODEL_PATH)
    logger.info("Carregant model des de %s...", model_path)
    artifacts = joblib.load(str(model_path))
    _model = artifacts["model"]
    _preprocessor = artifacts["preprocessor"]
    _feature_names = artifacts["feature_names"]
    _model_version = settings.APP_VERSION
    logger.info("Model carregat: %s", type(_model).__name__)


def frontend_available() -> bool:
    """Return whether the built SPA is available on disk."""
    return FRONTEND_INDEX.exists()


def frontend_file_response(path: Path) -> FileResponse:
    """Serve a file from the bundled frontend."""
    return FileResponse(path)


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

if FRONTEND_ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_ASSETS_DIR)), name="assets")


# ==================== ENDPOINTS ====================

@app.get("/")
def root():
    """Serve the SPA when available, otherwise return API info."""
    if frontend_available():
        return frontend_file_response(FRONTEND_INDEX)

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


@app.get("/predictions", tags=["Monitoring"])
async def get_predictions(limit: int = 100):
    """Retrieve recent predictions from the store."""
    try:
        predictions = find_all_predictions(limit=limit)
        return {
            "count": len(predictions),
            "predictions": predictions,
        }
    except Exception as exc:
        logger.error("Failed to read predictions: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to read prediction records") from exc


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: StudentDepressionInput):
    """
    Predicció de depressió per a un estudiant.

    Accepta un JSON validat per Pydantic amb les 14 features del dataset.
    Retorna la predicció (0/1), la probabilitat i la versió del model.
    """
    if _model is None or _preprocessor is None or _feature_names is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    features_dict = request.to_model_dict()
    X = pd.DataFrame([features_dict])[_feature_names]
    X_processed = _preprocessor.transform(X)
    prediction = int(_model.predict(X_processed)[0])

    probability = None
    if hasattr(_model, "predict_proba"):
        proba = _model.predict_proba(X_processed)[0]
        probability = float(proba[1])

    save_prediction(
        input_data=features_dict,
        prediction=prediction,
        probability=probability,
        model_version=_model_version or "unknown",
    )

    logger.info(
        "Prediction: %d | Probability: %s",
        prediction,
        f"{probability:.3f}" if probability is not None else "N/A",
    )

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
            "detail": str(exc),
        },
    )


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Fallback route for client-side navigation in the React SPA."""
    if not frontend_available():
        raise HTTPException(status_code=404, detail="Route not found")

    requested = FRONTEND_DIR / full_path
    if full_path and requested.exists() and requested.is_file():
        return frontend_file_response(requested)

    return frontend_file_response(FRONTEND_INDEX)
