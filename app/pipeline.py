"""
Pipeline ETL bàsic (Sessió 4)

Carrega el CSV de depressió estudiantil, fa validacions bàsiques,
i guarda en format Parquet.
"""

import pandas as pd
from pathlib import Path
import logging
import sys

from app.config import setup_logging

logger = logging.getLogger(__name__)

DEFAULT_INPUT = "data/raw/student_depression_dataset.csv"
DEFAULT_OUTPUT = "data/student_depression_clean.parquet"

EXPECTED_COLUMNS = [
    'id', 'Gender', 'Age', 'City', 'Profession',
    'Academic Pressure', 'Work Pressure', 'CGPA',
    'Study Satisfaction', 'Job Satisfaction', 'Sleep Duration',
    'Dietary Habits', 'Degree', 'Have you ever had suicidal thoughts ?',
    'Work/Study Hours', 'Financial Stress', 'Family History of Mental Illness',
    'Depression',
]


def load_csv(file_path: str) -> pd.DataFrame:
    """Carrega un fitxer CSV i mostra informació bàsica."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Fitxer no trobat: {file_path}")

    logger.info(f"Carregant dades de: {file_path}")
    df = pd.read_csv(file_path)
    logger.info(f"Dimensions: {df.shape[0]} files x {df.shape[1]} columnes")
    logger.info(f"Columnes: {list(df.columns)}")

    return df


def validate_basic(df: pd.DataFrame) -> bool:
    """Validació bàsica: columnes esperades, valors faltants i DataFrame buit."""
    is_valid = True

    # Check expected columns
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        logger.error(f"Columnes esperades no trobades: {missing_cols}")
        is_valid = False
    else:
        logger.info("Totes les columnes esperades presents")

    # Check missing values
    missing = df.isnull().sum()
    missing_present = missing[missing > 0]
    if len(missing_present) > 0:
        logger.warning("Valors faltants detectats:")
        for col, count in missing_present.items():
            pct = (count / len(df)) * 100
            logger.warning(f"  {col}: {count} ({pct:.1f}%)")
    else:
        logger.info("Cap valor faltant detectat")

    # Check Financial Stress special case ('?' values)
    if 'Financial Stress' in df.columns:
        invalid_fs = (df['Financial Stress'] == '?').sum()
        if invalid_fs > 0:
            logger.warning(
                f"  Financial Stress: {invalid_fs} valors '?' detectats "
                f"({invalid_fs / len(df) * 100:.1f}%)"
            )

    # Check target distribution
    if 'Depression' in df.columns:
        dist = df['Depression'].value_counts().to_dict()
        logger.info(f"Distribució de la variable target (Depression): {dist}")

    if df.empty:
        logger.error("El DataFrame està buit!")
        is_valid = False

    return is_valid


def save_parquet(df: pd.DataFrame, output_path: str) -> None:
    """Guarda el DataFrame en format Parquet."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(path, index=False)
    size_kb = path.stat().st_size / 1024
    logger.info(f"Guardat: {path} ({size_kb:.1f} KB, {len(df)} files)")


def run_pipeline(
    input_file: str = DEFAULT_INPUT,
    output_file: str = DEFAULT_OUTPUT,
) -> None:
    """Executa el pipeline ETL bàsic."""
    logger.info("=" * 50)
    logger.info("INICIANT PIPELINE ETL")
    logger.info("=" * 50)

    # Pas 1: Carregar
    logger.info("\n[Pas 1/2] Carregant dades...")
    df = load_csv(input_file)

    # Pas 2: Validar i guardar
    logger.info("\n[Pas 2/2] Validant i guardant...")
    is_valid = validate_basic(df)
    if not is_valid:
        logger.error("Validació fallida. Aturant pipeline.")
        sys.exit(1)

    save_parquet(df, output_file)

    logger.info("=" * 50)
    logger.info("PIPELINE COMPLETAT")
    logger.info("=" * 50)


# 🔮 SESSIONS FUTURES:
# Propera sessió: Afegirem normalització de columnes, splits de dades (60/20/20)
# i preprocessing (conversió de categòriques, imputació de '?' en Financial Stress)


if __name__ == "__main__":
    setup_logging(log_file="logs/pipeline.log")
    run_pipeline()
