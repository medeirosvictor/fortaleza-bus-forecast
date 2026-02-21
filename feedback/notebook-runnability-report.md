# Notebook Runnability — Remaining Issues

> Last updated: February 2026
> Python: 3.13.7 | pandas 2.3.3 | scikit-learn 1.8.0 | xgboost 3.2.0 | lightgbm 4.6.0

---

## 🔴 Blocker: Missing root-level data files

Notebooks `01-data-processing`, `02-data-visualization`, and `03-cross-year-comparison` read from **gitignored** CSVs at the project root:
- `./data_input_zerofill_2015.csv`
- `./data_input_zerofill_2018.csv`
- `./data_input_zerofill_2020.csv`
- `./data_input_nozerofill_2015.csv`

The processed versions exist in `model-data/` (filtered to top-100 lines, with features). The full zerofilled files are not in the repo.

**Fix:** Point notebooks at `model-data/` CSVs, or regenerate the zerofill files from raw data.

---

## 🔴 API Breakage: `pandas .append()` in scripts/zero_filler.py

`scripts/zero_filler.py` still has one `df.append()` call. This was **removed in pandas 2.0** (current: 2.3.3).

**Fix:** Replace with `pd.concat()`.

---

## 🟡 `other-related-notebooks/` — Need TensorFlow

All 3 neural network notebooks (07, 08, 09) import `tensorflow` and read `./df_input.csv` (doesn't exist). These are incomplete experiments.

**Fix:** `pip install tensorflow` if reviving them, plus figure out what `df_input.csv` was.

---

## ✅ Fixed (previously reported)

- ~~Root `variables.py` missing~~ — Removed; holidays now in `src/fortaleza_bus_forecast/data/holidays.py`
- ~~`OneHotEncoder(sparse=False)` deprecated~~ — Updated to `sparse_output=False`
- ~~Random seeds missing~~ — `RANDOM_SEED = 42` added to all relevant notebooks
