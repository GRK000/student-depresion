"""
Pydantic Schemas (Sessió 3)

Models per validació de requests/responses amb restriccions de domini.
"""

from pydantic import BaseModel, Field
from typing import Optional


class StudentDepressionInput(BaseModel):
    """Request schema per predicció de depressió en estudiants (14 features)."""

    age: float = Field(..., ge=18.0, le=60.0, description="Edat en anys (18-60)")
    academic_pressure: float = Field(..., ge=0.0, le=5.0, description="Pressió acadèmica (0-5)")
    work_pressure: float = Field(..., ge=0.0, le=5.0, description="Pressió laboral (0-5)")
    cgpa: float = Field(..., ge=0.0, le=10.0, description="Nota mitjana acumulativa (0-10)")
    study_satisfaction: float = Field(..., ge=0.0, le=5.0, description="Satisfacció amb els estudis (0-5)")
    job_satisfaction: float = Field(..., ge=0.0, le=4.0, description="Satisfacció laboral (0-4)")
    work_study_hours: float = Field(..., ge=0.0, le=12.0, description="Hores de treball/estudi per dia (0-12)")
    financial_stress: float = Field(..., ge=1.0, le=5.0, description="Estrès financer (1-5)")
    gender: str = Field(..., description="Gènere: 'Male' o 'Female'")
    sleep_duration: str = Field(..., description="Durada del son: \"'5-6 hours'\", \"'Less than 5 hours'\", \"'7-8 hours'\", \"'More than 8 hours'\", 'Others'")
    dietary_habits: str = Field(..., description="Hàbits alimentaris: 'Healthy', 'Moderate', 'Unhealthy', 'Others'")
    degree: str = Field(..., description="Grau acadèmic (p.ex. BSc, B.Tech, MBA, PhD...)")
    suicidal_thoughts: str = Field(..., description="Pensaments suïcides: 'Yes' o 'No'")
    family_history: str = Field(..., description="Historial familiar de malaltia mental: 'Yes' o 'No'")

    def to_model_dict(self) -> dict:
        """Converteix els camps al format que espera el model (noms originals amb espais)."""
        return {
            'Age': self.age,
            'Academic Pressure': self.academic_pressure,
            'Work Pressure': self.work_pressure,
            'CGPA': self.cgpa,
            'Study Satisfaction': self.study_satisfaction,
            'Job Satisfaction': self.job_satisfaction,
            'Work/Study Hours': self.work_study_hours,
            'Financial Stress': self.financial_stress,
            'Gender': self.gender,
            'Sleep Duration': self.sleep_duration,
            'Dietary Habits': self.dietary_habits,
            'Degree': self.degree,
            'Have you ever had suicidal thoughts ?': self.suicidal_thoughts,
            'Family History of Mental Illness': self.family_history,
        }

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "age": 28.0,
                "academic_pressure": 3.0,
                "work_pressure": 0.0,
                "cgpa": 7.03,
                "study_satisfaction": 5.0,
                "job_satisfaction": 0.0,
                "work_study_hours": 9.0,
                "financial_stress": 1.0,
                "gender": "Male",
                "sleep_duration": "'Less than 5 hours'",
                "dietary_habits": "Healthy",
                "degree": "BA",
                "suicidal_thoughts": "No",
                "family_history": "Yes"
            }]
        }
    }


class PredictionResponse(BaseModel):
    """Response schema per l'endpoint de predicció."""

    prediction: int = Field(..., description="Predicció binària: 0=sense depressió, 1=amb depressió")
    probability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confiança de la predicció")
    model_version: str = Field(..., description="Versió del model")


class HealthResponse(BaseModel):
    """Response schema per l'endpoint de health check."""

    status: str = Field(..., description="Estat del servei: 'healthy' o 'unhealthy'")
    model_loaded: bool = Field(..., description="Si el model està carregat")
    model_version: Optional[str] = Field(None, description="Versió del model carregat")


class ErrorResponse(BaseModel):
    """Response schema per errors."""

    error: str = Field(..., description="Tipus d'error")
    detail: str = Field(..., description="Detalls de l'error")
