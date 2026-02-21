"""
Preprocessor — Feature engineering for transit boarding prediction.

Functions to add holiday flags, one-hot encode day-of-week, apply cyclical
encoding, and compute derived temporal features.
"""

import numpy as np
import pandas as pd
import calendar
import datetime

from .holidays import get_holidays, get_holiday_eves


def add_holiday_flags(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Add binary 'feriado' and 'vespera_feriado' columns.

    Parameters:
        df:   DataFrame with 'd_mes' and 'mes' columns
        year: Year to look up holidays for

    Returns:
        DataFrame with 'feriado' and 'vespera_feriado' columns added.
    """
    df = df.copy()
    feriados = get_holidays(year)
    vesperas = get_holiday_eves(year)

    df["feriado"] = df.apply(
        lambda row: 1 if any(
            d == row["d_mes"] and m == row["mes"] for _, d, m in feriados
        ) else 0,
        axis=1,
    )
    df["vespera_feriado"] = df.apply(
        lambda row: 1 if any(
            d == row["d_mes"] and m == row["mes"] for _, d, m in vesperas
        ) else 0,
        axis=1,
    )
    return df


def add_onehot_dayofweek(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add one-hot encoded day-of-week columns (domingo..sabado).

    Expects a 'd_semana' column (0=Sunday/Monday depending on source).

    Returns:
        DataFrame with 7 new binary columns.
    """
    from sklearn.preprocessing import OneHotEncoder

    df = df.copy()
    encoder = OneHotEncoder(sparse_output=False)
    encoded = encoder.fit_transform(df["d_semana"].values.reshape(-1, 1))
    day_cols = ["domingo", "segunda", "terca", "quarta", "quinta", "sexta", "sabado"]

    # Only add as many columns as the encoder produced
    for i, col in enumerate(day_cols[:encoded.shape[1]]):
        df[col] = encoded[:, i]

    return df


def add_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add sin/cos cyclical encoding for temporal columns.

    Encodes: hora (24), d_semana (7), d_mes (31), d_ano (366),
             mes (12), semana_do_mes (4).

    Returns:
        DataFrame with *_sin and *_cos columns added.
    """
    df = df.copy()
    encodings = {
        "hora": 24,
        "d_semana": 7,
        "d_mes": 31,
        "d_ano": 366,
        "mes": 12,
        "semana_do_mes": 4,
    }
    # Also handle 'hour_sin'/'hour_cos' naming convention
    if "hora" in df.columns and "hour_sin" not in df.columns:
        df["hour_sin"] = np.sin(2 * np.pi * df["hora"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hora"] / 24)

    for col, max_val in encodings.items():
        if col in df.columns:
            df[f"{col}_sin"] = np.sin(2 * np.pi * df[col] / max_val)
            df[f"{col}_cos"] = np.cos(2 * np.pi * df[col] / max_val)

    return df


def week_of_month(tgtdate) -> int:
    """
    Return the week of the month (1-indexed) for a given date.

    Accepts pandas Timestamps and plain datetime objects.
    """
    if hasattr(tgtdate, "to_pydatetime"):
        tgtdate = tgtdate.to_pydatetime()

    days_this_month = calendar.mdays[tgtdate.month]
    for i in range(1, days_this_month):
        d = datetime.datetime(tgtdate.year, tgtdate.month, i)
        if d.day - d.weekday() > 0:
            startdate = d
            break

    return (tgtdate - startdate).days // 7 + 1


def prepare_features(
    df: pd.DataFrame,
    year: int,
    cyclical: bool = False,
) -> pd.DataFrame:
    """
    Full feature engineering pipeline: holidays + one-hot OR cyclical encoding.

    Parameters:
        df:       Raw DataFrame with temporal columns
        year:     Year for holiday lookup
        cyclical: If True, use cyclical encoding; otherwise one-hot day-of-week

    Returns:
        DataFrame ready for model training.
    """
    df = add_holiday_flags(df, year)

    if cyclical:
        df = add_cyclical_features(df)
    else:
        df = add_onehot_dayofweek(df)
        # Ensure hour sin/cos exist
        if "hour_sin" not in df.columns and "hora" in df.columns:
            df["hour_sin"] = np.sin(2 * np.pi * df["hora"] / 24)
            df["hour_cos"] = np.cos(2 * np.pi * df["hora"] / 24)

    return df
