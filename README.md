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
u
vicorn app.api:app --reload
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

### Mètriques del model actiu (v2)

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
│   ├── model_v2.pkl              # ← model actiu (.env)
│   ├── metadata_v2.json          # deployment_ready: true
│   └── model_v3.pkl / metadata_v3.json  # Versions posteriors
├── logs/
├── .env
├── requirements.txt
└── README.md
```

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
