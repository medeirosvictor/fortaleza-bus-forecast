"""
Data Loader — Read processed CSVs into DataFrames.

Handles year-specific file paths and datetime parsing.
"""

import os
import pandas as pd

from ..config import DATA_DIR, TARGET_COL, SUPPORTED_YEARS


def load_year_data(year: int, data_dir: str = None) -> pd.DataFrame:
    """
    Load the processed dataset for a given year.

    Parameters:
        year:     One of 2015, 2018, 2020
        data_dir: Override data directory (default: project's model-data/)

    Returns:
        DataFrame with parsed datetime column.
    """
    if year not in SUPPORTED_YEARS:
        raise ValueError(f"Year {year} not supported. Choose from {SUPPORTED_YEARS}")

    base_dir = data_dir or DATA_DIR
    filepath = os.path.join(base_dir, str(year), f"top100_lines_{year}.csv")

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"No data file found for year {year} at {filepath}. "
            f"Run 'make data' to extract the datasets."
        )

    df = pd.read_csv(filepath)

    if "data_hora" in df.columns:
        df["data_hora"] = pd.to_datetime(df["data_hora"], errors="coerce")

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
