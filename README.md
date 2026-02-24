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

### `Financial Stress` — gestió de valors `'?'`

El dataset conté 3 files amb el valor literal `'?'` a `Financial Stress`. Es converteix la columna a numèrica amb `pd.to_numeric(..., errors='coerce')` (els `'?'` passen a `NaN`) i després s'eliminen les 3 files afectades amb `dropna()`. Representar menys del 0,01 % de les dades, l'eliminació no afecta significativament el model.

### Split train/test

Divisió 80/20 amb `stratify=y` per preservar la proporció de positius i negatius en ambdós subconjunts. `random_state=42` per reproduïbilitat.
