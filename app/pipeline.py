"""
Pipeline ETL bàsic (Sessió 4)

Carrega el CSV de depressió estudiantil, fa validacions bàsiques,
i guarda en format Parquet.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys

from sklearn.model_selection import train_test_split
from app.config import setup_logging

logger = logging.getLogger(__name__)

DEFAULT_INPUT = "data/raw/student_depression_dataset.csv"
DEFAULT_OUTPUT = "data/student_depression_clean.parquet"

RANDOM_SEED = 42
TRAIN_RATIO = 0.60
VAL_RATIO = 0.20
PROD_RATIO = 0.20

EXPECTED_COLUMNS = [
    'Gender', 'Age', 'Academic Pressure', 'Work Pressure', 'CGPA',
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


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalitza el dataset Student Depression.

    - Elimina columnes de metadades: id, City, Profession
    - Converteix Financial Stress '?' a NaN i elimina files afectades
    - Assegura que el target (Depression) és enter binari
    """
    df = df.copy()

    # Eliminar columnes de metadades que no aportem al model
    cols_to_drop = [c for c in ['id', 'City', 'Profession'] if c in df.columns]
    if cols_to_drop:
        logger.info(f"Eliminant columnes de metadades: {cols_to_drop}")
        df = df.drop(columns=cols_to_drop)

    # Financial Stress pot contenir '?' — convertir a NaN
    if 'Financial Stress' in df.columns:
        before = df['Financial Stress'].isna().sum()
        df['Financial Stress'] = pd.to_numeric(df['Financial Stress'], errors='coerce')
        after = df['Financial Stress'].isna().sum()
        new_nans = after - before
        if new_nans > 0:
            logger.warning(f"  Financial Stress: {new_nans} valors '?' convertits a NaN")

    # Eliminar files amb NaN
    before = len(df)
    df = df.dropna()
    dropped = before - len(df)
    if dropped > 0:
        logger.info(f"Eliminades {dropped} files amb valors nuls")

    # Assegurar que Depression és int binari
    if 'Depression' in df.columns:
        df['Depression'] = df['Depression'].astype(int)
        logger.info(f"Target (Depression) assegurat com a binari: {sorted(df['Depression'].unique())}")

    logger.info(f"Columnes resultants ({len(df.columns)}): {list(df.columns)}")
    return df


def create_splits(df: pd.DataFrame) -> tuple:
    """
    Crea splits estratificats 60/20/20: training, validation, production.

    Estratègia en dos passos:
    1. Separar training (60%) de la resta (40%)
    2. Dividir la resta en validation (20%) i production (20%)

    Returns:
        tuple: (train_df, val_df, prod_df)
    """
    stratify_col = 'Depression' if 'Depression' in df.columns else None
    stratify = df[stratify_col] if stratify_col else None

    # Pas 1: Separar training (60%)
    train_df, rest_df = train_test_split(
        df,
        test_size=1 - TRAIN_RATIO,
        random_state=RANDOM_SEED,
        stratify=stratify,
    )

    # Pas 2: Dividir la resta en validation (50%) i production (50%)
    stratify_rest = rest_df[stratify_col] if stratify_col else None
    val_df, prod_df = train_test_split(
        rest_df,
        test_size=0.5,
        random_state=RANDOM_SEED,
        stratify=stratify_rest,
    )

    total = len(df)
    logger.info("Splits creats:")
    logger.info(f"  Training:   {len(train_df):5d} files ({len(train_df)/total:.1%})")
    logger.info(f"  Validation: {len(val_df):5d} files ({len(val_df)/total:.1%})")
    logger.info(f"  Production: {len(prod_df):5d} files ({len(prod_df)/total:.1%})")

    return train_df, val_df, prod_df


def save_splits(train_df: pd.DataFrame, val_df: pd.DataFrame,
                prod_df: pd.DataFrame, output_dir: str = "data") -> None:
    """Guarda els tres splits com a fitxers Parquet."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for name, split_df in [
        ('training_set', train_df),
        ('validation_set', val_df),
        ('production_set', prod_df),
    ]:
        path = out / f'{name}.parquet'
        split_df.to_parquet(path, index=False)
        size_kb = path.stat().st_size / 1024
        logger.info(f"  Guardat: {path} ({size_kb:.1f} KB, {len(split_df)} files)")


def run_pipeline(
    input_file: str = DEFAULT_INPUT,
    output_file: str = DEFAULT_OUTPUT,
) -> None:
    """Executa el pipeline ETL bàsic."""
    logger.info("=" * 50)
    logger.info("INICIANT PIPELINE ETL")
    logger.info("=" * 50)

    # Pas 1: Carregar
    logger.info("\n[Pas 1/4] Carregant dades...")
    df = load_csv(input_file)

    # Pas 2: Normalitzar columnes
    logger.info("\n[Pas 2/4] Normalitzant columnes...")
    df = normalize_columns(df)

    # Pas 3: Validar
    logger.info("\n[Pas 3/4] Validant...")
    is_valid = validate_basic(df)
    if not is_valid:
        logger.error("Validació fallida. Aturant pipeline.")
        sys.exit(1)

    # Pas 4: Crear splits i guardar
    logger.info("\n[Pas 4/4] Creant splits 60/20/20...")
    train_df, val_df, prod_df = create_splits(df)
    save_splits(train_df, val_df, prod_df)

    logger.info("=" * 50)
    logger.info("PIPELINE COMPLETAT")
    logger.info("=" * 50)


# 🔮 SESSIONS FUTURES:
# Propera sessió: Afegirem normalització de columnes, splits de dades (60/20/20)
# i preprocessing (conversió de categòriques, imputació de '?' en Financial Stress)


if __name__ == "__main__":
    setup_logging(log_file="logs/pipeline.log")
    run_pipeline()
