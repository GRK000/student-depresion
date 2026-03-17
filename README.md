# Student Depression Prediction API

API de predicció de risc de depressió en estudiants, construïda amb FastAPI i scikit-learn.

---

## Quick Start

```bash
# 1. Instal·lar dependències
pip install -r requirements.txt

# 2. Generar els splits de dades
python -m app.pipeline

# 3. Entrenar el model (genera la propera versió automàticament)
python -m app.train

# 4. Actualitzar .env amb la versió generada
# MODEL_PATH=models/model_vN.pkl
# METADATA_PATH=models/metadata_vN.json

# 5. Arrencar l'API
uvicorn app.api:app --reload
```

---

## Dataset

**Nom:** Student Depression Dataset  
**Font:** [Kaggle — Student Depression Dataset](https://www.kaggle.com/datasets/hopesb/student-depression-dataset)  
**Mida:** 27.901 files × 18 columnes (27.898 usables — 3 files eliminades per valors `'?'` en `Financial Stress`)  
**Problema:** Classificació binària — predir si un estudiant pateix depressió (`Depression`: 0 = no, 1 = sí)

---

## Features usades i target

S'han seleccionat 14 de les 18 columnes originals. Les columnes descartades (`id`, `City`, `Profession`) no aporten informació predictiva (identificadors o metadades).

### Features numèriques (8)

| Columna | Descripció | Rang |
|---------|-----------|------|
| `Age` | Edat de l'estudiant | 18–59 |
| `Academic Pressure` | Pressió acadèmica percebuda | 0–5 |
| `Work Pressure` | Pressió laboral percebuda | 0–5 |
| `CGPA` | Nota mitjana acumulativa | 0–10 |
| `Study Satisfaction` | Satisfacció amb els estudis | 0–5 |
| `Job Satisfaction` | Satisfacció laboral | 0–4 |
| `Work/Study Hours` | Hores diàries de treball o estudi | 0–12 |
| `Financial Stress` | Nivell d'estrès financer | 1–5 |

### Features categòriques (6)

| Columna | Valors possibles |
|---------|-----------------|
| `Gender` | `Male`, `Female` |
| `Sleep Duration` | `'Less than 5 hours'`, `'5-6 hours'`, `'7-8 hours'`, `'More than 8 hours'`, `Others` |
| `Dietary Habits` | `Healthy`, `Moderate`, `Unhealthy`, `Others` |
| `Degree` | 28 valors (BSc, B.Tech, MBA, PhD, etc.) |
| `Have you ever had suicidal thoughts ?` | `Yes`, `No` |
| `Family History of Mental Illness` | `Yes`, `No` |

### Target

| Columna | Tipus | Descripció |
|---------|-------|-----------|
| `Depression` | `int` (0/1) | 0 = sense depressió, 1 = amb depressió |

Distribució del target: **58,5 % positius** (16.336) / **41,5 % negatius** (11.565) — lleugerament desbalancejat.

---

## Decisions de preprocessament

### Features numèriques → `StandardScaler`

Les 8 features numèriques s'escalen amb **StandardScaler** (mitjana 0, desviació estàndard 1). Motiu: la Regressió Logística és sensible a la magnitud de les variables — sense escalat, `CGPA` (rang 0–10) tindria molt menys pes que `Age` (rang 18–59) únicament per diferència d'escala, distorsionant els coeficients.

### Features categòriques → `OrdinalEncoder`

Les 6 features categòriques s'encoden amb **OrdinalEncoder** (`handle_unknown='use_encoded_value'`, `unknown_value=-1`). Motiu: la Regressió Logística requereix entrades numèriques. S'usa `OrdinalEncoder` en lloc de `OneHotEncoder` per evitar l'explosió de dimensions amb `Degree` (28 categories). Els valors desconeguts s'encoden com a `-1` per robustesa en producció.

### `Financial Stress` — gestió de valors `'?'`

El dataset conté 3 files amb el valor literal `'?'` a `Financial Stress`. Es converteix la columna a numèrica amb `pd.to_numeric(..., errors='coerce')` (els `'?'` passen a `NaN`) i després s'eliminen les 3 files afectades amb `dropna()`. Representar menys del 0,01 % de les dades, l'eliminació no afecta significativament el model.

### Splits del pipeline — 60/20/20

El dataset s'ha dividit en tres conjunts estratificats sobre `Depression`:

| Conjunt | Proporció | Mida | Ús |
|---------|-----------|------|----|
| `training_set.parquet` | 60 % | 16.738 | Entrenament del model |
| `validation_set.parquet` | 20 % | 5.580 | Quality gate (avaluació) |
| `production_set.parquet` | 20 % | 5.580 | Simulació de producció |

---

## Quality Gate i Model Versioning

Cada execució de `python -m app.train` genera automàticament la propera versió disponible (`v1`, `v2`, `v3`, …) sense sobreescriure versions anteriors. El model s'avalua sobre el `validation_set.parquet` i es compara amb els criteris de `config/deployment_criteria.yaml`:

```yaml
deployment_criteria:
  min_precision: 0.75   # Context de salut mental: recall > precision
  min_recall: 0.70      # Falsos negatius (depressió no detectada) costen més
  min_f1_score: 0.72
  min_roc_auc: 0.80
```

El resultat es guarda a `models/metadata_vN.json` amb el flag `deployment_ready: true/false`. Només s'actualitza `.env` si `deployment_ready` és `true`.

### Mètriques del model actiu (v3)

| Mètrica | Valor |
|---------|-------|
| Accuracy | 85,52 % |
| Precision | 86,47 % |
| Recall | 89,23 % |
| F1 Score | 87,83 % |
| ROC-AUC | 92,55 % |

---

## Persistència de prediccions

Cada crida a `POST /predict` guarda un registre a `data/predictions.jsonl` (format JSON Lines):

```json
{
  "timestamp": "2026-03-03T15:45:37.196332",
  "input": {"Age": 22, "Gender": "Female", ...},
  "prediction": 1,
  "probability": 0.834,
  "model_version": "1.0.0"
}
```

L'historial es pot consultar via `GET /predictions?limit=N` sense accedir al sistema de fitxers.

---

## Endpoints de l'API

| Mètode | Path | Descripció |
|--------|------|-----------|
| `GET` | `/` | Informació bàsica |
| `GET` | `/health` | Estat del servei i model carregat |
| `POST` | `/predict` | Predicció de depressió (valida amb Pydantic) |
| `GET` | `/predictions` | Historial de prediccions (monitoratge) |
| `GET` | `/docs` | Documentació interactiva (Swagger UI) |

---

## Estructura del projecte

```text
mlops/
├── app/
│   ├── __init__.py
│   ├── api.py          # FastAPI: endpoints /health, /predict, /predictions
│   ├── config.py       # pydantic-settings: MODEL_PATH, METADATA_PATH, PREDICTIONS_LOG_PATH
│   ├── pipeline.py     # ETL: CSV → normalize → validate → splits 60/20/20 (Parquet)
│   ├── pred_store.py   # Persistència JSON Lines de prediccions
│   ├── predict.py      # CLI: predicció per línia de comandes
│   ├── schemas.py      # Pydantic: StudentDepressionInput, PredictionResponse
│   └── train.py        # Entrenament: versioning + quality gate + metadades JSON
├── tests/
│   ├── __init__.py          # Package marker
│   ├── conftest.py          # Fixtures: client, temp_predictions_log, loaded_model
│   ├── test_api.py          # 6 tests: health, predict, errors 422, logging
│   ├── test_model.py        # 2 tests: càrrega model, format predicció
│   └── test_pipeline.py     # 4 tests: normalize_columns, schema Pydantic
├── config/
│   └── deployment_criteria.yaml  # Criteris mínims de qualitat
├── data/
│   ├── raw/
│   │   └── student_depression_dataset.csv
│   ├── training_set.parquet
│   ├── validation_set.parquet
│   ├── production_set.parquet
│   └── predictions.jsonl         # Generat en execució
├── models/
│   ├── model_v1.pkl              # Model sessió 5 (sense metadades)
│   ├── model_v2.pkl / metadata_v2.json
│   └── model_v3.pkl / metadata_v3.json  # ← model actiu (.env/.env.production)
├── logs/
├── .env
├── .env.production              # Entorn CI/CD comès al repositori
├── .cicd/
│   └── hooks/
│       ├── validate.sh          # Phase 1: make docker-test
│       └── pre-deploy.sh        # Phase 2: comprova deployment_ready
├── compose.yml                   # Docker Compose: servei, ports, volums
├── Dockerfile                    # Multi-stage: base → test → production
├── .dockerignore
├── Makefile                      # Automatització: setup, test, docker-up, health, predict
├── requirements.txt
└── README.md
```

---

## Docker

### Arquitectura multi-stage

El `Dockerfile` té tres stages:

| Stage | Contingut | Ús |
|-------|-----------|-----|
| `base` | Sistema + deps Python + `appuser` (UID 1000) | Base compartida |
| `test` | Copia tot el projecte, executa `pytest` | Quality gate |
| `production` | Copia `app/` + `models/` + `config/` com a `appuser` | Imatge final |

El servei s'executa com a usuari **no-root** (`appuser`), eliminant un vector d'atac si hi ha vulnerabilitats al codi.

### Workflow amb Makefile

El `Makefile` centralitza totes les operacions del projecte:

```bash
make help           # Llista tots els targets disponibles

make setup          # Crea .venv i instal·la dependències
make test           # Executa pytest (12 tests: pipeline, model, API)
make pipeline       # Genera els splits de dades (Parquet)
make train          # Entrena el model (auto-versioning + quality gate)

make docker-build   # Construeix la imatge (docker compose build)
make docker-up      # Arrenca el servei (crea data/ logs/, ajusta permisos, compose up -d)
make docker-down    # Para el servei (docker compose down)
make docker-test    # Executa tests dins del contenidor Docker

make health         # Comprova GET /health → JSON formatat
make predict        # Fa una predicció de prova → JSON formatat

make dev            # Arrenca l'API localment amb hot-reload (sense Docker)
make clean          # Elimina .venv, __pycache__, parquets, logs
```

### Arrencar el servei

```bash
# Workflow complet des de zero
make docker-build
make docker-up

# Verificar
make health
# {"status": "healthy", "model_loaded": true, "model_version": "1.0.0"}

make predict
# {"prediction": 0, "probability": 0.043, "model_version": "1.0.0"}
```

### compose.yml — configuració declarativa

```yaml
name: mlops

services:
  api:
    build:
      context: .
      target: production      # Stage multi-stage a construir
    ports:
      - "${PORT:-8083}:8000"  # Port llegit de .env (default 8083)
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs      # Logs persistents a l'amfitrió
      - ./data:/app/data      # predictions.jsonl persistent
    restart: unless-stopped
```

Substitueix el `docker run` amb cinc flags per configuració versionada al repositori. Qualsevol persona que cloni el repo pot arrencar el servei amb `make docker-up` sense llegir documentació addicional.

### Verificar persistència de prediccions

```bash
make docker-up
make predict                            # Escriu 1 línia a data/predictions.jsonl
wc -l data/predictions.jsonl           # Compte línies

make docker-down && make docker-up     # Restart complet
wc -l data/predictions.jsonl           # Ha de tenir el mateix nombre de línies
```

### Verificar l'usuari no-root

```bash
docker run --rm student-depression-api whoami
# appuser
```

### Verificar el HEALTHCHECK automàtic

```bash
docker compose ps
# CONTAINER ID   STATUS                    PORTS
# mlops-api-1    Up 2 minutes (healthy)    0.0.0.0:8083->8000/tcp
```

Docker comprova `/health` cada 30 s (configurat al `Dockerfile`). El servei passa a `healthy` ~10 s després d'arrencar.

### Aturar el servei

```bash
make docker-down
```

---

## Testing

Suite de 12 tests automatitzats amb `pytest`, organitzats en tres àrees:

### Tests de pipeline i schema (4 tests — `test_pipeline.py`)

| Test | Què verifica |
|------|-------------|
| `test_normalize_columns_drops_metadata` | `normalize_columns` elimina `id`, `City`, `Profession` |
| `test_normalize_columns_keeps_features` | Manté les 14 features + `Depression` target |
| `test_schema_validation_valid` | `StudentDepressionInput` accepta dades vàlides |
| `test_schema_validation_invalid_age` | Rebutja `age > 60` amb `ValidationError` |

### Tests de model (2 tests — `test_model.py`)

| Test | Què verifica |
|------|-------------|
| `test_model_loads_successfully` | El `.pkl` conté `model`, `preprocessor`, `feature_names` |
| `test_model_prediction_format` | Predicció és 0/1, probabilitats en [0, 1] |

### Tests d'API (6 tests — `test_api.py`)

| Test | Què verifica |
|------|-------------|
| `test_health_endpoint` | `GET /health` → 200, `status: "healthy"` |
| `test_predict_valid_input` | `POST /predict` → 200, predicció + probabilitat |
| `test_predict_missing_field` | Camps faltants → 422 |
| `test_predict_invalid_range` | `age: 150` → 422 |
| `test_predict_returns_model_version` | Resposta inclou `model_version` no buit |
| `test_predict_logs_to_file` | Predicció s'escriu al fitxer JSONL (integració) |

### Aïllament de tests

- **`temp_predictions_log` (autouse=True):** Cada test escriu a un fitxer temporal, mai al `predictions.jsonl` real
- **`client` (scope="session"):** El `TestClient` inicialitza el `lifespan` de FastAPI (càrrega del model) una sola vegada
- **`loaded_model` (scope="session"):** El model es carrega una sola vegada per a tots els tests de model

### Executar els tests

```bash
# Localment (12 tests)
make test

# Dins del contenidor Docker (stage test)
make docker-test
```

---

## CI/CD Validació (Sessió 12)

La validació s'executa al servidor en cada `git push`:

1. **Phase 1 (`validate.sh`)**
  - copia `.env.production` a `.env`
  - executa `make docker-test`
2. **Phase 2 (`pre-deploy.sh`)**
  - llegeix `METADATA_PATH`
  - valida `deployment_ready` del JSON de metadades

> Separació clau: `git push` **valida**; el desplegament real amb tags s'implementa a la sessió següent.

### Fitxers de la sessió

- `.env.production`
- `.cicd/hooks/validate.sh`
- `.cicd/hooks/pre-deploy.sh`

### Verificació local abans de fer push

```bash
bash .cicd/hooks/validate.sh
bash .cicd/hooks/pre-deploy.sh
```

Si `pre-deploy.sh` falla, el model no és desplegable (`deployment_ready=false`).

---

## Checkpoint de sessions

- [x] **Sessió 1** — CLI de predicció (`predict.py` + `argparse`)
- [x] **Sessió 2** — API FastAPI (`/health`, `/predict`) + model `LogisticRegression`
- [x] **Sessió 3** — Validació Pydantic (`schemas.py`: `StudentDepressionInput`)
- [x] **Sessió 4** — Configuració centralitzada (`config.py` + `.env`) + pipeline ETL bàsic
- [x] **Sessió 5** — Pipeline complet: splits 60/20/20 estratificats → Parquet
- [x] **Sessió 6** — README documentat
- [x] **Sessió 7** — Model versioning + quality gate (`deployment_criteria.yaml`) + metadades JSON
- [x] **Sessió 8** — Persistència de prediccions (`pred_store.py`) + endpoint `GET /predictions`
- [x] **Sessió 9** — Docker single-stage (`Dockerfile` + `.dockerignore` + imatge verificada)
- [x] **Sessió 10** — Docker multi-stage (base → production, usuari no-root) + `compose.yml` + `Makefile`
- [x] **Sessió 11** — Testing: 12 tests pytest (pipeline/schema + model + API) + stage `test` al Dockerfile
- [x] **Sessió 12** — CI/CD validació: `.env.production` + hooks `validate.sh` i `pre-deploy.sh`
