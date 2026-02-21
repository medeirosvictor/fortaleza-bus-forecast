# ==============================================================================
# Data Builder — Parses raw fare validation CSVs into hourly aggregated counts
#
# Purpose: Raw data from Fortaleza's fare system contains one row per card tap.
# This script aggregates them into hourly passenger counts per bus line and
# extracts temporal features (hour, day of week, month, etc.) used by ML models.
#
# Input:  ./raw-2015/*.csv  (one CSV per day of raw fare validations)
# Output: ../data_input_nozerofill_2015.csv  (aggregated, but without zero-filled gaps)
#
# Raw CSV format (semicolon-separated, no header):
#   777;84;Siqueira/Messejana/P;2001;06/01/2015 09:21:03;2;02-ESTUDANTE ETUFOR;Ida;N;
#   Fields: unknown, line_number, line_name, bus_id, datetime, unknown2,
#           validation_type, direction, transfer_flag
# ==============================================================================

import os
from os import path
import pandas as pd
from datetime import datetime
from multiprocessing import Pool
import dateutil.parser
import numpy as np
import datetime
import calendar

# Import shared utility — single source of truth for week_of_month
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module as _im
_hf = _im('helper-funs')
week_of_month = _hf.week_of_month

final_df = pd.DataFrame()


def fill_header(val_do_dia, filename):
    """Write raw data with proper column headers and re-read as DataFrame."""
    val_do_dia.to_csv('dfs_2015/' + filename, header=[
        'undf', 'linha', 'linha_nome', 'id_onibus', 'data_hora',
        'undf2', 'tipo_validacao', 'sentido', 'integracao'
    ], index=False)
    df = pd.read_csv('dfs_2015/' + filename)
    return df


def encode(data, col, max_val):
    """Apply sin/cos cyclical encoding to a column."""
    data[col + '_sin'] = np.sin(2 * np.pi * data[col] / max_val)
    data[col + '_cos'] = np.cos(2 * np.pi * data[col] / max_val)
    return data


def generate_df(filename):
    """Process one day's raw CSV into aggregated hourly counts per line."""
    encoding = False

    print(filename)
    val = pd.read_csv('./raw-2015/' + filename, sep=';')
    val = val.drop('Unnamed: 9', axis=1)
    val.reset_index(drop=True, inplace=True)

    validation_georeffed_do_dia = fill_header(val, filename)

    # Cast column types
    validation_georeffed_do_dia['linha'] = validation_georeffed_do_dia['linha'].astype(str)
    validation_georeffed_do_dia['linha_nome'] = validation_georeffed_do_dia['linha_nome'].astype(str)
    validation_georeffed_do_dia['undf'] = validation_georeffed_do_dia['undf'].astype(str)

    # Parse datetime and floor to the hour (aggregate granularity)
    validation_georeffed_do_dia['data_hora'] = pd.to_datetime(
        validation_georeffed_do_dia['data_hora'],
        format='%d/%m/%Y %H:%M:%S', errors='coerce'
    )
    validation_georeffed_do_dia['data_hora'] = validation_georeffed_do_dia['data_hora'].dt.floor('H')

    validation_georeffed_do_dia['tipo_validacao'] = validation_georeffed_do_dia['tipo_validacao'].astype(str)
    validation_georeffed_do_dia['sentido'] = validation_georeffed_do_dia['sentido'].astype(str)
    validation_georeffed_do_dia['integracao'] = validation_georeffed_do_dia['integracao'].astype(str)

    # Aggregate: count validations per (line, hour)
    validation_georeffed_do_dia = pd.DataFrame(
        {'validacoes_por_hora': validation_georeffed_do_dia.groupby(['linha', 'data_hora']).size()}
    ).reset_index()

    # Extract temporal features
    validation_georeffed_do_dia['d_semana'] = validation_georeffed_do_dia.apply(
        lambda row: row.data_hora.dayofweek, axis=1
    )
    validation_georeffed_do_dia["d_mes"] = validation_georeffed_do_dia['data_hora'].dt.day
    validation_georeffed_do_dia["d_ano"] = validation_georeffed_do_dia['data_hora'].dt.dayofyear
    validation_georeffed_do_dia["mes"] = validation_georeffed_do_dia['data_hora'].dt.month
    validation_georeffed_do_dia["semana_do_mes"] = validation_georeffed_do_dia['data_hora'].apply(week_of_month)
    validation_georeffed_do_dia["hora"] = validation_georeffed_do_dia['data_hora'].dt.strftime('%H').astype(int)

    # Optional: apply cyclical encoding
    if encoding:
        encode(validation_georeffed_do_dia, 'd_mes', 31)
        encode(validation_georeffed_do_dia, 'd_semana', 6)
        encode(validation_georeffed_do_dia, 'd_ano', 366)
        encode(validation_georeffed_do_dia, 'mes', 12)
        encode(validation_georeffed_do_dia, 'semana_do_mes', 4)
        encode(validation_georeffed_do_dia, 'hora', 23)

    global final_df
    final_df = pd.concat([final_df, validation_georeffed_do_dia], ignore_index=True)
    print(len(final_df))


if __name__ == '__main__':
    all_files = os.listdir('./raw-2015/')

    for filename in all_files:
        generate_df(filename)

    final_df.to_csv(f'../data_input_nozerofill_2015.csv', sep=',', index=False)
