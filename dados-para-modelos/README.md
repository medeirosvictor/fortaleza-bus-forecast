# Model-Ready Datasets

Pre-processed CSV files used by the ML notebooks. Each file contains the **top 100 bus lines** by ridership volume, zero-filled, with temporal features and holiday flags.

## Data Source

- **Provider:** ETUFOR (Empresa de Transporte Urbano de Fortaleza)
- **Type:** Electronic fare validation data (smart card taps) from Fortaleza's public bus transit system
- **Processing pipeline:** Raw CSVs → `helper_scripts/data_builder.py` → `helper_scripts/zero_filler.py` → filtered to top 100 lines → holiday/day-of-week flags added in notebooks

## Files

| File | Year | Rows | Period | Notes |
|------|------|------|--------|-------|
| `2015/top100_linhas_data_model_2015.csv` | 2015 | 414,688 | Jan 2015 – Jan 2016 | Full year + ~12 days into 2016 |
| `2018/top100_linhas_data_model_2018.csv` | 2018 | 511,509 | Jan – Aug 2018 | ⚠️ Only 8 months of data available |
| `2020/top100_linhas_data_model.csv` | 2020 | 756,593 | Mar 2020 – Jan 2021 | ⚠️ No Jan/Feb data; COVID-19 impact from March onward |

## ⚠️ Data Limitations

- **2018 is incomplete** — only January through August. The raw data provided by ETUFOR did not include September–December.
- **2020 starts in March** — January and February 2020 data was not collected/provided. The zero-filler added rows for those months, but they represent fabricated zeros, not actual zero ridership.
- **2020 includes COVID-19 pandemic** — Fortaleza's lockdown began mid-March 2020. Ridership dropped dramatically. Cross-year comparisons involving 2020 should account for this.
- **"Bilhete Único" effect** — Fortaleza's integrated fare system (allowing multiple bus transfers within 2 hours for a single fare) was adopted gradually. During the adoption period, ridership numbers show unusual growth patterns that don't reflect organic demand changes.

## Column Definitions

All three files share the same 20-column schema (comma-separated):

| Column | Type | Description |
|--------|------|-------------|
| `linha` | int | Bus line number (e.g., 41, 325) |
| `data_hora` | datetime | Timestamp floored to the hour |
| `validations_per_hour` | int | **Target variable** — passenger boarding count for this line+hour |
| `d_semana` | int | Day of week (0=Monday … 6=Sunday) |
| `hour_sin` | float | sin(2π × hour / 23) — cyclical encoding of hour |
| `hour_cos` | float | cos(2π × hour / 23) — cyclical encoding of hour |
| `hora` | int | Hour of day (0–23) |
| `d_mes` | int | Day of month (1–31) |
| `d_ano` | int | Day of year (1–366) |
| `mes` | int | Month (1–12) |
| `semana_do_mes` | int | Week of month (1-indexed) |
| `domingo` | int | 1 if Sunday, else 0 |
| `segunda` | int | 1 if Monday, else 0 |
| `terca` | int | 1 if Tuesday, else 0 |
| `quarta` | int | 1 if Wednesday, else 0 |
| `quinta` | int | 1 if Thursday, else 0 |
| `sexta` | int | 1 if Friday, else 0 |
| `sabado` | int | 1 if Saturday, else 0 |
| `feriado` | int | 1 if national/local holiday, else 0 |
| `vespera_feriado` | int | 1 if eve of a holiday, else 0 |

## Obtaining Raw Data

The raw fare validation CSVs are not included in this repository due to size (~1 GB+). They were provided directly by ETUFOR for academic research purposes. Contact ETUFOR or Fortaleza's Secretaria de Infraestrutura for data access requests.
