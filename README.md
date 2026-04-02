# Student Wellbeing Assessment

Aplicación full-stack para evaluar indicadores de bienestar emocional en estudiantes mediante:

- una API de inferencia en `FastAPI`
- un pipeline de entrenamiento y comparación de modelos
- una interfaz web conversacional en `React`

La herramienta es orientativa. No sustituye una valoración profesional ni emite un diagnóstico clínico.

---

## Stack

### Backend y ML

- Python `3.11.2`
- FastAPI
- scikit-learn
- XGBoost
- pandas / pyarrow
- pytest

### Frontend

- React
- Vite
- Tailwind CSS
- Framer Motion
- Lucide Icons

---

## Qué Hace El Proyecto

El proyecto recoge 14 variables del dataset de depresión en estudiantes y genera una predicción binaria de riesgo.

Actualmente incluye:

- pipeline ETL con splits estratificados `60/20/20`
- comparación de modelos entre `Logistic Regression`, `Random Forest` y `XGBoost`
- selección del mejor candidato con criterio `recall-first`
- quality gate para decidir si el modelo está listo para despliegue
- persistencia de predicciones en `JSON Lines`
- frontend conversacional con landing, evaluación guiada, resultados y página explicativa

---

## Quick Start

### 1. Backend

Requisito recomendado:

```bash
python --version
# 3.11.2
```

Instalación y ejecución:

```bash
pip install -r requirements.txt
python -m app.pipeline
python -m app.train
uvicorn app.api:app --reload
```

Después de entrenar, revisa `.env` para apuntar al modelo activo:

```env
MODEL_PATH=models/model_vN.pkl
METADATA_PATH=models/metadata_vN.json
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

En PowerShell de Windows, si `npm` falla por execution policy, usa:

```powershell
npm.cmd run dev
```

Por defecto el frontend espera la API en:

```text
http://localhost:8083
```

Se puede cambiar con:

```bash
VITE_API_BASE_URL=http://localhost:8083
```

---

## Dataset

- Nombre: `Student Depression Dataset`
- Fuente: [Kaggle - Student Depression Dataset](https://www.kaggle.com/datasets/hopesb/student-depression-dataset)
- Tamaño original: `27,901` filas y `18` columnas
- Tamaño usable: `27,898` filas
- Problema: clasificación binaria sobre `Depression`

Se eliminan 3 filas por valores literales `'?'` en `Financial Stress`.

---

## Variables Del Modelo

Se usan 14 features. Se descartan `id`, `City` y `Profession`.

### Numéricas

| Feature | Rango |
| --- | --- |
| `Age` | 18-59 |
| `Academic Pressure` | 0-5 |
| `Work Pressure` | 0-5 |
| `CGPA` | 0-10 |
| `Study Satisfaction` | 0-5 |
| `Job Satisfaction` | 0-4 |
| `Work/Study Hours` | 0-12 |
| `Financial Stress` | 1-5 |

### Categóricas

| Feature | Valores |
| --- | --- |
| `Gender` | `Male`, `Female` |
| `Sleep Duration` | `Less than 5 hours`, `5-6 hours`, `7-8 hours`, `More than 8 hours`, `Others` |
| `Dietary Habits` | `Healthy`, `Moderate`, `Unhealthy`, `Others` |
| `Degree` | múltiples categorías |
| `Have you ever had suicidal thoughts ?` | `Yes`, `No` |
| `Family History of Mental Illness` | `Yes`, `No` |

### Target

| Campo | Significado |
| --- | --- |
| `Depression` | `0 = no`, `1 = sí` |

Distribución aproximada del target:

- `58.5%` positivos
- `41.5%` negativos

---

## Preprocesamiento

### Numéricas

- `StandardScaler` para `Logistic Regression`
- `passthrough` para `Random Forest` y `XGBoost`

### Categóricas

- `OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)`

### Valores inválidos

- `Financial Stress` se convierte con `pd.to_numeric(..., errors="coerce")`
- las filas con `NaN` resultante se eliminan

### Splits

| Split | Proporción | Uso |
| --- | --- | --- |
| `training_set.parquet` | 60% | entrenamiento |
| `validation_set.parquet` | 20% | evaluación y quality gate |
| `production_set.parquet` | 20% | simulación de producción |

---

## Núcleo Científico

El entrenamiento ya no usa un único modelo. `python -m app.train` compara:

- `Logistic Regression`
- `Random Forest`
- `XGBoost`

La selección del modelo ganador sigue este orden:

1. modelos que pasan el quality gate
2. `recall`
3. `f1_score`
4. `roc_auc`
5. `precision`
6. `accuracy`

Esto es intencional: en este contexto el coste de un falso negativo es mayor que el de un falso positivo.

### Métricas Generadas

Cada entrenamiento calcula y guarda:

- `accuracy`
- `precision`
- `recall`
- `f1_score`
- `roc_auc`
- matriz de confusión
- análisis de falsos positivos
- análisis de falsos negativos
- importancia global de variables

### Artefactos Generados

Cada ejecución de `python -m app.train` genera:

- `models/model_vN.pkl`
- `models/metadata_vN.json`
- `models/report_vN.md`

El artefacto `.pkl` mantiene compatibilidad con la API actual.

### Quality Gate

Configurado en [`config/deployment_criteria.yaml`](/d:/IA/mlops/config/deployment_criteria.yaml):

```yaml
deployment_criteria:
  min_precision: 0.75
  min_recall: 0.70
  min_f1_score: 0.72
  min_roc_auc: 0.80
```

Si el modelo no supera el gate, `deployment_ready` queda en `false`.

---

## API

### Endpoints

| Método | Path | Descripción |
| --- | --- | --- |
| `GET` | `/` | información básica |
| `GET` | `/health` | estado del servicio y modelo cargado |
| `POST` | `/predict` | predicción de riesgo |
| `GET` | `/predictions` | historial reciente de predicciones |
| `GET` | `/docs` | Swagger UI |

### Ejemplo de predicción

```json
{
  "age": 28.0,
  "academic_pressure": 3.0,
  "work_pressure": 0.0,
  "cgpa": 7.03,
  "study_satisfaction": 5.0,
  "job_satisfaction": 0.0,
  "work_study_hours": 9.0,
  "financial_stress": 1.0,
  "gender": "Male",
  "sleep_duration": "Less than 5 hours",
  "dietary_habits": "Healthy",
  "degree": "BA",
  "suicidal_thoughts": "No",
  "family_history": "Yes"
}
```

### Persistencia De Predicciones

Cada llamada a `POST /predict` escribe un registro en:

- `data/predictions.jsonl`

Formato:

```json
{
  "timestamp": "2026-03-03T15:45:37.196332",
  "input": {
    "Age": 22
  },
  "prediction": 1,
  "probability": 0.834,
  "model_version": "1.0.0"
}
```

---

## Frontend

El frontend vive en [`frontend/`](/d:/IA/mlops/frontend).

### Pantallas

- `Home`: landing y modal de aceptación
- `Assessment`: chat guiado con progreso
- `Results`: resultado, factores influyentes y recomendaciones
- `About`: cómo funciona, límites y responsabilidad

### Comportamiento

- recoge las 14 variables reales del backend
- traduce la conversación a payload estructurado
- hace `POST /predict` al backend
- si la API no responde, usa una estimación local de respaldo para no romper la experiencia

### Diseño

Dirección visual implementada:

- minimalista
- mucho aire
- bordes redondeados
- sombras suaves
- tono calmado y cercano

La UI está construida con:

- componentes `ui/`
- componentes de chat en `components/chat/`
- componentes de resultados en `components/result/`

---

## Docker

El backend está dockerizado. El frontend, por ahora, se ejecuta fuera de Docker.

### Build y arranque

```bash
make docker-build
make docker-up
make health
make predict
```

### Compose

[`compose.yml`](/d:/IA/mlops/compose.yml) expone la API y monta:

- `./logs:/app/logs`
- `./data:/app/data`

### Seguridad

El contenedor de producción usa usuario no root:

- `appuser`

---

## Testing

Actualmente hay 17 tests automatizados:

- `tests/test_pipeline.py`: 4 tests
- `tests/test_model.py`: 2 tests
- `tests/test_api.py`: 6 tests
- `tests/test_train.py`: 5 tests

### Ejecutar tests

```bash
make test
make docker-test
```

### Qué cubren

- pipeline y normalización de datos
- validación de schema
- carga del modelo
- formato de predicción
- endpoints de la API
- logging de predicciones
- lógica de selección de modelos
- análisis de errores del entrenamiento

---

## CI/CD

El pipeline CI/CD actual cubre validación y despliegue del backend:

| Fase | Hook | Qué hace |
| --- | --- | --- |
| 1 | `validate.sh` | ejecuta tests en Docker |
| 2 | `pre-deploy.sh` | verifica `deployment_ready == true` |
| 3 | `deploy.sh` | reconstruye y levanta el servicio |
| 4 | `post-deploy.sh` | valida `/health` y prueba una predicción |

El frontend aún no está integrado en Docker ni en el pipeline de despliegue.

---

## Estructura Del Proyecto

```text
mlops/
├── app/
│   ├── api.py
│   ├── config.py
│   ├── pipeline.py
│   ├── pred_store.py
│   ├── predict.py
│   ├── schemas.py
│   └── train.py
├── config/
│   └── deployment_criteria.yaml
├── data/
│   ├── raw/
│   ├── training_set.parquet
│   ├── validation_set.parquet
│   ├── production_set.parquet
│   └── predictions.jsonl
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   └── styles/
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── models/
│   ├── model_v*.pkl
│   ├── metadata_v*.json
│   └── report_v*.md
├── tests/
│   ├── test_api.py
│   ├── test_model.py
│   ├── test_pipeline.py
│   └── test_train.py
├── Dockerfile
├── Makefile
├── compose.yml
├── requirements.txt
└── README.md
```

---

## Estado Actual

Backend:

- pipeline ETL completo
- comparación de modelos implementada
- quality gate activo
- API funcional
- Docker y CI/CD para backend

Frontend:

- interfaz conversacional implementada
- build de producción verificado con `npm run build`
- integración básica con la API lista
- no desplegado aún dentro del flujo Docker/CI

Interpretabilidad avanzada:

- hay importancia global de variables
- SHAP y explicaciones individuales aún no están implementados

---

## Próximos Pasos Naturales

- integrar SHAP o una alternativa visual equivalente
- devolver explicaciones reales desde el backend para cada predicción
- conectar el chat con un LLM para extracción más flexible de señales
- dockerizar y desplegar también el frontend
- añadir tests de frontend

