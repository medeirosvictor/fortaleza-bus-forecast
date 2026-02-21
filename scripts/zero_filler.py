# ==============================================================================
# Zero Filler — Inserts missing (line, hour) rows with 0 validations
#
# Purpose: The raw fare validation data only contains rows where at least one
# passenger tapped their card. Hours with zero boardings are simply absent.
# This script explicitly inserts 0-count rows for every missing hour so that
# ML models can learn "no passengers" rather than treating it as missing data.
#
# Input:  ../data_input_nozerofill_2015.csv  (output of data_builder.py)
# Output: ../data_input_zerofill_2015_top10_ciclycal.csv  (zero-filled, with cyclical features)
# ==============================================================================

import os
import pandas as pd
from calendar import monthrange
from math import ceil
import numpy as np
import datetime as dt

# Import shared utility — single source of truth for week_of_month
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module as _im
_hf = _im('helper-funs')
week_of_month = _hf.week_of_month

data = pd.read_csv('../data_input_nozerofill_2015.csv', sep=',', delimiter=',')
data_model = data.copy()

# Use only the top 100 lines (lines with the most recorded validations)
top100_linhalist = data_model.groupby(data_model.linha).sum().reset_index().sort_values(
    'validacoes_por_hora', ascending=False
).index[:5].to_list()


def encode(data, col, max_val):
    """Apply sin/cos cyclical encoding to a column."""
    data[col + '_sin'] = np.sin(2 * np.pi * data[col] / max_val)
    data[col + '_cos'] = np.cos(2 * np.pi * data[col] / max_val)
    return data


for linha in top100_linhalist:
    print("Line: ", linha)
    currentDataModel_Linha = data_model.loc[data_model.linha == linha]

    for mes in range(1, 13):
        print(mes)
        currentDataModel_Mes = currentDataModel_Linha.loc[currentDataModel_Linha.mes == mes]
        dia_max = monthrange(2020, mes)[1]

        for dia in range(1, dia_max + 1):
            currentDataModel_Dia = currentDataModel_Mes.loc[currentDataModel_Mes.d_mes == dia]

            for hora in range(0, 24):
                currentDataModel_Hora = currentDataModel_Dia[currentDataModel_Dia.hora == hora]

                if currentDataModel_Hora.empty == False:
                    continue
                else:
                    # Skip invalid dates (e.g., Feb 29 in non-leap years)
                    if (mes == 2 and dia > 28):
                        continue

                    dd = dt.datetime.strptime(
                        '2015-' + str(mes) + '-' + str(dia) + ' ' + str(hora) + ':00:00',
                        "%Y-%m-%d %H:00:00"
                    )

                    new_row = {
                        'linha': linha,
                        'data_hora': dd,
                        'validacoes_por_hora': 0,
                        'd_semana': dd.weekday(),
                        'd_mes': dia,
                        'd_ano': dd.timetuple().tm_yday,
                        'mes': mes,
                        'semana_do_mes': week_of_month(dd),
                        'hora': hora,

                        'd_mes_sin': np.sin(2 * np.pi * dia / 31),
                        'd_mes_cos': np.cos(2 * np.pi * dia / 31),

                        'd_semana_sin': np.sin(2 * np.pi * dd.weekday() / 7),
                        'd_semana_cos': np.cos(2 * np.pi * dd.weekday() / 7),

                        'd_ano_sin': np.sin(2 * np.pi * dd.timetuple().tm_yday / 366),
                        'd_ano_cos': np.cos(2 * np.pi * dd.timetuple().tm_yday / 366),

                        'mes_sin': np.sin(2 * np.pi * mes / 12),
                        'mes_cos': np.cos(2 * np.pi * mes / 12),

                        'semana_do_mes_sin': np.sin(2 * np.pi * week_of_month(dd) / 4),
                        'semana_do_mes_cos': np.cos(2 * np.pi * week_of_month(dd) / 4),

                        'hora_sin': np.sin(2 * np.pi * hora / 23),
                        'hora_cos': np.cos(2 * np.pi * hora / 23)
                    }

                    # pd.concat replaces deprecated df.append() (removed in pandas 2.0)
                    data_model = pd.concat([data_model, pd.DataFrame([new_row])], ignore_index=True)

data_model = data_model.sort_values(['linha', 'data_hora'], ascending=[True, True])
data_model.to_csv('../data_input_zerofill_2015_top10_ciclycal.csv', index=False, sep=';')
