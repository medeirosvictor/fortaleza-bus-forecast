# Notebook Runnability Report

> Last updated: February 2026
> Python: 3.13.7 | pandas 2.3.3 | scikit-learn 1.8.0 | xgboost 3.2.0 | lightgbm 4.6.0

---

## Current Status

All main notebooks in `notebooks/` read from `model-data/` (extracted via `make data`) and are **runnable independently**.

| Notebook | Status | Notes |
|----------|--------|-------|
| `02-data-visualization.ipynb` | ✅ Runnable | EDA, seasonality plots |
| `03-cross-year-comparison.ipynb` | ✅ Runnable | Cross-year ensemble models |
| `04-results.ipynb` | ✅ Runnable | Reads pre-computed predictions from `predict-vs-real/` |
| `05-per-line-models.ipynb` | ✅ Runnable | Core modeling (smoke tested: R²=0.906 on line 41) |
| `06-per-line-models-cyclical.ipynb` | ✅ Runnable | Cyclical feature variant |
| `01-data-processing.ipynb` | ⚠️ Reference only | Needs raw `data_input_nozerofill_*.csv` (not in repo) |
| `experimental/07-09` | ⚠️ Broken | Need TensorFlow + missing `df_input.csv` |

---

## 🟡 Remaining Minor Issues

### `notebooks/experimental/` — Need TensorFlow

All 3 neural network notebooks (07, 08, 09) import `tensorflow` and read `./df_input.csv` (doesn't exist). These are incomplete experiments from the thesis that were never finalized.

**Fix:** `pip install tensorflow`, figure out what `df_input.csv` was, or just leave them as historical artifacts.

---

## ✅ Previously Fixed

- ~~Notebooks read missing root-level CSVs~~ → All point to `model-data/` now
- ~~`pandas .append()` in zero_filler.py~~ → Replaced with `pd.concat()`
- ~~`OneHotEncoder(sparse=False)` deprecated~~ → Updated to `sparse_output=False`
- ~~Random seeds missing~~ → `RANDOM_SEED = 42` added to all relevant notebooks
- ~~Root `variables.py` missing~~ → Removed; holidays in `src/fortaleza_bus_forecast/data/holidays.py`
- ~~2015 data only had 71 lines~~ → Regenerated with 100 lines
- ~~2018 dates bleeding into 2020~~ → Filtered to 2018 only
- ~~2020 fabricated Jan/Feb zeros~~ → Removed, Mar–Dec only
