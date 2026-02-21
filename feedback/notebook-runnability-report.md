# Notebook Runnability Report

> Date: February 2026
> Python: 3.13.7 | pandas 2.3.3 | scikit-learn 1.8.0 | xgboost 3.2.0 | lightgbm 4.6.0

---

## 🔴 Blocker: Missing root-level data files

All main notebooks read from **gitignored** CSVs at the project root:
- `./data_input_zerofill_2015.csv` (used by Comparativo-Anos, Data-Visualization)
- `./data_input_zerofill_2018.csv` (same)
- `./data_input_zerofill_2020.csv` (same)
- `./data_input_nozerofill_2015.csv` (used by Tratamento-de-Dados)

**But** the processed versions exist in `dados-para-modelos/`. These are the *output* of Tratamento-de-Dados (filtered to top-100 lines, with features). The full zerofilled files are gone.

**Fix:** Either regenerate from `dados-para-modelos/` CSVs (they already have all features including holiday flags, one-hot days), or point notebooks at those files directly.

---

## 🔴 Blocker: Missing `variables.py` at root

`Comparativo-Anos.ipynb` does `from variables import day_of_week_translator, feriados, vesperas` — no year suffix. A root-level `variables.py` existed (there's a `__pycache__/variables.cpython-38.pyc`) but was deleted. The only surviving one is `2015/variables.py`, which exports `feriados_2015`, `feriados_2018`, etc. (with year suffixes).

**Fix:** Create a root `variables.py` that re-exports with the generic names, or update the notebook import.

---

## 🔴 API Breakage: `pandas .append()` removed

`helper_scripts/zero_filler.py`, `2015/Modelo-PorLinha-2015.ipynb`, and `Comparativo-Anos.ipynb` all use `df.append()`, which was **removed in pandas 2.0** (current: 2.3.3).

**Fix:** Replace `data_model = data_model.append(new_row, ignore_index=True)` with `data_model = pd.concat([data_model, pd.DataFrame([new_row])], ignore_index=True)`.

---

## 🔴 API Breakage: `OneHotEncoder(sparse=False)`

`Comparativo-Anos.ipynb` and `Modelo-PorLinha-2015.ipynb` use `sparse=False`, which was **renamed to `sparse_output=False`** in scikit-learn 1.2+ (current: 1.8.0).

**Fix:** `OneHotEncoder(sparse=False)` → `OneHotEncoder(sparse_output=False)`.

---

## 🟡 `other-related-notebooks/` — Need TensorFlow

All 3 neural network notebooks import `tensorflow` and read `./df_input.csv` (doesn't exist). These are the least complete notebooks — likely experiments that weren't pursued for the thesis.

**Fix:** `pip install tensorflow` if you want to revive them, plus figure out what `df_input.csv` was.

---

## 🟢 `Resultados.ipynb` — Mostly runnable

Reads from `predict-vs-real/` CSVs. Two paths point to root-level files that don't exist (`predict-vs-real/linha41_1mes(3)_2semanas(4)_predict.csv`), but the year-subfolder versions do exist. Quick path fix.

---

## 🟢 `2015/Modelo-PorLinha-2015.ipynb` — Closest to runnable

Imports from local `variables.py` (exists in `2015/`), but reads the missing zerofill CSVs via `../data_input_zerofill_2015.csv`. Needs the `.append()` and `sparse` fixes. This is the core modeling notebook and the one most worth fixing first.

---

## Summary: 4 fixes to get the main notebooks running

1. Recreate root `variables.py` (or symlink to `2015/variables.py` with aliases)
2. Point data paths at `dados-para-modelos/` CSVs (or regenerate the zerofill files)
3. `.append()` → `pd.concat()`
4. `sparse=False` → `sparse_output=False`
