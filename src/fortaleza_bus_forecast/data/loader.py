"""
Data Loader — Read processed CSVs into DataFrames.

Handles year-specific file paths, delimiter detection, and datetime parsing.
"""

import os
import pandas as pd

from ..config import DATA_DIR, PROJECT_ROOT, TARGET_COL, SUPPORTED_YEARS


def load_year_data(year: int, zerofilled: bool = True, data_dir: str = None) -> pd.DataFrame:
    """
    Load the processed dataset for a given year.

    Parameters:
        year:       One of 2015, 2018, 2020
        zerofilled: If True, load the zero-filled version (default)
        data_dir:   Override data directory (default: project's dados-para-modelos/)

    Returns:
        DataFrame with parsed datetime column and consistent column names.
    """
    if year not in SUPPORTED_YEARS:
        raise ValueError(f"Year {year} not supported. Choose from {SUPPORTED_YEARS}")

    base_dir = data_dir or DATA_DIR

    # Try dados-para-modelos first, then project root
    candidates = [
        os.path.join(base_dir, str(year), f"top100_linhas_data_model_{year}.csv"),
        os.path.join(base_dir, str(year), f"top100_linhas_data_model_{year}_ciclycal.csv"),
        os.path.join(PROJECT_ROOT, f"data_input_zerofill_{year}.csv"),
        os.path.join(PROJECT_ROOT, f"data_input_nozerofill_{year}.csv"),
    ]

    if not zerofilled:
        # Prefer non-zerofilled
        candidates = [
            os.path.join(PROJECT_ROOT, f"data_input_nozerofill_{year}.csv"),
        ] + candidates

    filepath = None
    for c in candidates:
        if os.path.exists(c):
            filepath = c
            break

    if filepath is None:
        raise FileNotFoundError(
            f"No data file found for year {year}. "
            f"Searched: {candidates}"
        )

    # Detect delimiter
    with open(filepath, "r") as f:
        first_line = f.readline()
    delimiter = ";" if ";" in first_line else ","

    df = pd.read_csv(filepath, delimiter=delimiter)

    # Parse datetime
    if "data_hora" in df.columns:
        df["data_hora"] = pd.to_datetime(
            df["data_hora"],
            format="%Y/%m/%d %H:%M:%S",
            errors="coerce",
        )
        # Fallback for other date formats
        mask = df["data_hora"].isna()
        if mask.any():
            df.loc[mask, "data_hora"] = pd.to_datetime(
                df.loc[mask, "data_hora"], errors="coerce"
            )

    # Normalize target column name
    if "validacoes_por_hora" in df.columns and TARGET_COL not in df.columns:
        df = df.rename(columns={"validacoes_por_hora": TARGET_COL})

    return df


def load_line_data(year: int, line: int, **kwargs) -> pd.DataFrame:
    """
    Load data for a specific bus line in a given year.

    Parameters:
        year: One of 2015, 2018, 2020
        line: Bus line number (e.g., 41, 325)

    Returns:
        DataFrame filtered to the specified line.
    """
    df = load_year_data(year, **kwargs)
    line_df = df[df["linha"] == line].copy()
    if line_df.empty:
        available = sorted(df["linha"].unique())
        raise ValueError(
            f"Line {line} not found in {year} data. "
            f"Available lines: {available[:20]}{'...' if len(available) > 20 else ''}"
        )
    return line_df
