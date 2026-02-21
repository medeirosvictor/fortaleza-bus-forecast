# AGENTS.md

This file provides guidance to AI coding agents (Claude Code, pi, etc.) when working with code in this repository.

## Project Overview

Undergraduate thesis (TCC) project: **Prediction and Data Analysis of Passenger Onboarding in Fortaleza's Public Bus Transit System** (Ceará, Brazil). Uses machine learning to predict hourly passenger boarding counts per bus line, using features like time of day, day of week, month, holidays, and cyclical encodings.

Data comes from Fortaleza's bus fare validation system (card tap data) across three years: **2015**, **2018**, and **2020**.

**University:** Universidade de Fortaleza (UNIFOR) — Centro de Ciências Tecnológicas, Curso de Ciência da Computação. Advisor: Prof. Dr. Carlos Caminha.

### Data Coverage Limitations
- **2015:** Full year (Jan–Dec)
- **2018:** Only **Jan–Jul** (7 months — Aug–Dec data was not provided by ETUFOR)
- **2020:** Only **Mar–Dec** (no Jan/Feb data; COVID-19 lockdown started mid-March)

## Pipeline

```
Raw CSV data (fare validations)
  → scripts/data_builder.py           # Parse, aggregate by line+hour, extract temporal features
  → scripts/zero_filler.py            # Fill missing hour slots with 0 validations
  → data_input_zerofill_YYYY.csv      # Complete dataset (gitignored)
  → model-data/                       # Filtered top-100 bus lines, model-ready CSVs
  → notebooks/ (training, evaluation) # Per-line models, cross-year comparison
  → performances/                     # CSV results (R², RMSE, MAE, MAPE)
  → predict-vs-real/                  # Predicted vs actual values for plotting
  → images/                           # Generated plots (PDFs, PNGs)
```

## Data Model

Each row in the processed dataset represents **one bus line in one hour**:

| Column | Description |
|--------|-------------|
| `linha` | Bus line number (e.g., 41, 325) |
| `data_hora` | Datetime floored to hour |
| `validations_per_hour` | **Target variable** — passenger count |
| `hora` | Hour of day (0–23) |
| `d_semana` | Day of week (0=Monday … 6=Sunday) |
| `d_mes` | Day of month |
| `d_ano` | Day of year |
| `mes` | Month (1–12) |
| `semana_do_mes` | Week of month |
| `hour_sin`, `hour_cos` | Cyclical encoding of hour |
| `feriado` | Binary — is it a holiday? |
| `vespera_feriado` | Binary — is it the eve of a holiday? |
| One-hot day-of-week columns | `domingo`, `segunda`, … `sabado` |

## Project Structure

```
notebooks/
  01-data-processing.ipynb            # Data pipeline reference (needs raw data)
  02-data-visualization.ipynb         # EDA — seasonality plots (hourly, daily, weekly, monthly)
  03-cross-year-comparison.ipynb      # Cross-year comparison, stacking ensemble, XGBoost
  04-results.ipynb                    # Aggregated results visualization, scatter plots
  05-per-line-models.ipynb            # Per-line models (Linear Reg, Ridge, SVR, Decision Tree,
                                      # Random Forest, Bagging, XGBoost, LightGBM, Stacking)
  06-per-line-models-cyclical.ipynb   # Same but with sin/cos cyclical feature encoding
  experimental/                       # Neural network experiments (need TensorFlow)

src/fortaleza_bus_forecast/           # Reusable Python package
  config.py                           # Feature lists, constants, paths, supported years
  data/
    holidays.py                       # Holiday/eve definitions for 2015/2018/2020
    loader.py                         # Load processed CSVs into DataFrames
    preprocessor.py                   # Feature engineering: holidays, one-hot, cyclical
  models/
    evaluator.py                      # Metrics (R², RMSE, MAE, MAPE), baseline predictions
    trainer.py                        # Model suite builder, train_and_evaluate, train_per_line
  visualization/
    plots.py                          # Thesis-quality plots: pred vs actual, hourly, comparisons

scripts/
  data_builder.py                     # Raw CSV → aggregated hourly validations per line
  zero_filler.py                      # Fills missing (line, hour) combos with 0
  helper-funs.py                      # Shared utils: get_performance(), week_of_month()

model-data/                           # Pre-processed CSVs for top-100 lines (extract with make data)
performances/                         # Model performance CSVs (per line, per config)
predict-vs-real/                      # Prediction output CSVs for plotting
images/                               # Generated visualizations (PDFs)
feedback/                             # Improvement notes and analysis
```

## ML Models Used

| Model | Library |
|-------|---------|
| Linear Regression | scikit-learn |
| Ridge Regression | scikit-learn |
| SVR (Support Vector Regression) | scikit-learn |
| Decision Tree Regressor | scikit-learn |
| Random Forest Regressor | scikit-learn |
| Bagging (Decision Tree) | scikit-learn |
| Gradient Boosting | scikit-learn |
| XGBoost | xgboost |
| LightGBM | lightgbm |
| Stacking Ensemble (XGB meta) | scikit-learn |

## Evaluation Metrics

- **R²** (coefficient of determination)
- **RMSE** (root mean squared error)
- **MAE** (mean absolute error)
- **MAPE** (mean absolute percentage error)

Computed via `src/fortaleza_bus_forecast/models/evaluator.py`.

## Feature Engineering Notes

- **Cyclical encoding**: Hour, day-of-week, day-of-month, day-of-year, month, and week-of-month are optionally encoded as `sin`/`cos` pairs to preserve circular continuity.
- **Holiday flags**: Brazilian national + Ceará/Fortaleza local holidays defined in `src/fortaleza_bus_forecast/data/holidays.py`.
- **Zero-filling**: Hours with no validations are explicitly inserted as 0-count rows so models learn "no passengers" vs "missing data."
- **Per-line models**: Each bus line gets its own trained model.
- **Training strategy**: Train on N months, predict a fixed future period. Experiments vary training window size and prediction horizon.

## Important Conventions

- Data CSVs are shipped as `model-data/data.zip` — run `make data` to extract.
- All notebooks live in `notebooks/` and can be run independently (no ordering required).
- Notebooks import shared logic from `src/fortaleza_bus_forecast/` via `sys.path.insert(0, '../src')`.
- Python 3.10+ with pandas, scikit-learn, xgboost, lightgbm, matplotlib, seaborn, numpy.
- Install the package with `pip install -e ".[full]"` or use `PYTHONPATH=src`.
