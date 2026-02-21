# Agent-User Feedback — Critical Analysis

> Project: Onboarding Prediction & Data Analysis for Fortaleza Bus Transit
> Context: Undergraduate thesis (TCC), Brazil
> Date: February 2026

---

## Overall Impression

This is a solid undergraduate thesis project tackling a real-world problem — predicting passenger boarding on Fortaleza's bus system using ML. The choice of a public transit dataset, the variety of models explored, and the attention to feature engineering (cyclical encoding, holiday flags, zero-filling) show genuine effort and curiosity. The `todo.txt` is honestly endearing — it reads like a snapshot of the thesis-writing grind that every Brazilian CS student knows well.

That said, looking at it now with fresh eyes, there are clear areas where the project could be modernized, hardened, and extended. Below are three phases of improvement, ordered from quick wins to ambitious expansions.

---

## What Works Well

- **Real-world data** from Fortaleza's transit system — not a toy dataset
- **Multiple model comparison** (10+ algorithms) with consistent metrics (R², RMSE, MAE, MAPE)
- **Cyclical feature encoding** (sin/cos) — shows understanding beyond basic one-hot
- **Holiday/eve-of-holiday flags** — domain-specific feature engineering that matters for transit
- **Zero-filling strategy** — correctly distinguishes "no passengers" from "no data"
- **Cross-year analysis** (2015, 2018, 2020) — attempts to study temporal generalization
- **Per-line model strategy** — pragmatic given the heterogeneity of bus lines

## What Needs Work

- **No reproducibility** — no `requirements.txt`, no environment specification, no seeds documented
- **Column naming inconsistency** — Portuguese/English mix across notebooks and years
- **No modular Python codebase** — all logic lives in notebooks with heavy duplication
- **No automated pipeline** — manual notebook execution order, no Makefile or orchestration
- **Data leakage risk** — train/test splits are time-based (good!) but not always consistently applied
- **2020 data includes COVID** — acknowledged in `todo.txt` but not controlled for in the analysis
- **No statistical significance testing** — model comparisons are point estimates only
- **Missing README documentation** — the README barely describes the project

---

## Phase 1: Housekeeping & Reproducibility (Low effort, high impact) ✅ COMPLETE

**Goal:** Make the project runnable by anyone, clean up technical debt.

### 1.1 — Environment & Dependencies ✅
- ~~Add `requirements.txt` or `pyproject.toml` with pinned versions~~ ✅ `requirements.txt` added
- ~~Add a `README.md` rewrite in English~~ ✅ Full README with EN + PT-BR sections, results table, methodology, project structure
- ~~Document Python version~~ ✅ Python 3.10+ in README

### 1.2 — Naming Consistency ✅
- ~~Rename notebook files to follow a clear numbering~~ ✅ All 9 notebooks renamed (`01-data-processing.ipynb` through `09-neural-net-standard.ipynb`)
- ~~Standardize column names~~ ✅ Model-ready CSVs in `dados-para-modelos/` use consistent schema (20 columns, `validations_per_hour`, `hour_sin`/`hour_cos`)
- Note: Intermediate pipeline files still have naming inconsistencies (`hora_sin` vs `hour_sin`) — documented but not fixed since they're not used by notebooks directly

### 1.3 — Code Deduplication ✅
- ~~The `variables.py` with holidays is duplicated~~ ✅ Root `variables.py` re-exports from `2015/variables.py` (single source of truth)
- ~~`week_of_month()` defined in 3 files~~ ✅ Canonical definition in `helper-funs.py`, imported by `data_builder.py` and `zero_filler.py`
- Note: `helper_scripts/modeling.py` extraction deferred — the model training loops are tightly coupled to notebook-specific logic and not easily extractable without risking breakage

### 1.4 — Random Seeds & Reproducibility ✅
- ~~Set `random_state` on every model~~ ✅ Notebooks 03, 05, 06, 09 already had `random_state`; added `RANDOM_SEED = 42` + `np.random.seed()` to notebooks 07 and 08 (+ `tf.random.set_seed()` for TF notebooks)
- Notebooks 01, 02, 04 are data processing/visualization — no randomness involved

### 1.5 — Git Hygiene ✅
- ~~`.ipynb_checkpoints/` tracked~~ ✅ Added to `.gitignore` (also `__pycache__/`)
- ~~Add data README~~ ✅ `dados-para-modelos/README.md` added with: data source, column definitions, date range limitations, how to obtain raw data

### Additional Phase 1 Work Done
- ✅ All Python files have English header comment blocks
- ✅ All notebooks have English markdown headers with purpose descriptions
- ✅ Portuguese inline comments translated to English across all notebooks
- ✅ Portuguese markdown cells translated in notebooks 02, 05, 06
- ✅ University name corrected from UFC → UNIFOR throughout
- ✅ Data coverage limitations documented (2018=8 months, 2020=no Jan/Feb, COVID impact)
- ✅ Thesis PDF analyzed — findings in `feedback/data-and-thesis-analysis.md`

---

## Phase 2: Methodological Improvements (Medium effort, high scientific value)

**Goal:** Strengthen the analysis and results for potential publication or portfolio showcase.

### 2.1 — Proper Time-Series Cross-Validation
- Replace ad-hoc "train on month X, predict month Y" with `sklearn.model_selection.TimeSeriesSplit`
- Implement walk-forward validation: train on [Jan], predict [Feb]; train on [Jan–Feb], predict [Mar]; etc.
- This eliminates any accidental data leakage and gives confidence intervals on metrics

### 2.2 — Statistical Significance
- Add confidence intervals (bootstrap) or paired t-tests when comparing models
- A model with MAE 12.3 vs 12.5 — is that significant or noise? Currently impossible to tell
- Report mean ± std across cross-validation folds, not single-split results

### 2.3 — COVID-Aware Analysis for 2020
- Either exclude 2020 from the main comparison or add a "COVID impact" section
- 2020 data without controlling for the pandemic is misleading — ridership dropped 60-80% in many cities
- Could be interesting: train on pre-COVID, predict during COVID, measure the "anomaly"

### 2.4 — Feature Importance Analysis
- Add SHAP values or permutation importance for the best-performing models
- Which features actually drive predictions? Hour and day-of-week probably dominate — prove it
- This adds interpretability, which matters for transit planning stakeholders

### 2.5 — Hyperparameter Tuning Rigor
- `RandomizedSearchCV` is used but the search spaces and number of iterations aren't well-documented
- Log all hyperparameter search results, not just the best model
- Consider Optuna or Bayesian optimization for XGBoost/LightGBM

### 2.6 — Baseline Models
- Add naive baselines: "predict the average for this line+hour+day-of-week" and "predict last week's same hour"
- If XGBoost only beats the naive baseline by 5%, that's important context

---

## Phase 3: Architecture & Extension (High effort, portfolio/production value)

**Goal:** Transform from a thesis notebook into a reusable, extensible project.

### 3.1 — Modular Python Package
- Restructure into a proper Python package:
  ```
  src/
    fortaleza_transit/
      data/
        loader.py          # Read raw CSVs
        preprocessor.py    # Zero-fill, feature engineering
        holidays.py        # Holiday definitions (all years)
      models/
        trainer.py         # Train any model with consistent interface
        evaluator.py       # Metrics computation, result logging
      visualization/
        plots.py           # Standardized plot generation
      config.py            # Feature lists, constants, paths
  notebooks/               # Thin notebooks that import from src/
  ```
- Notebooks become thin orchestration layers, not code repositories

### 3.2 — Experiment Tracking
- Add MLflow or Weights & Biases for experiment tracking
- Log every run: model type, hyperparameters, features used, train/test split, all metrics
- Makes it trivial to compare 100+ experiments and find the best configuration

### 3.3 — Multi-Line Modeling Strategy
- Currently: one model per bus line (scales poorly — 100+ models to maintain)
- Add experiments with:
  - **One global model** with `linha` as a feature (or embedding)
  - **Cluster-based models** — group lines by ridership volume (high/medium/low) as noted in `todo.txt`
  - Compare per-line vs global vs clustered performance

### 3.4 — Modern ML Approaches
- Try gradient-boosted models with native categorical support (CatBoost, LightGBM categorical mode)
- Explore Prophet or NeuralProphet for the time-series framing — they handle holidays and seasonality natively
- Consider a simple LSTM or Transformer for the time-series approach (the neural network notebooks seem incomplete)

### 3.5 — Interactive Dashboard
- Build a Streamlit or Gradio app that:
  - Lets users pick a bus line, date, and hour
  - Shows the predicted passenger count with confidence interval
  - Displays historical patterns for that line
  - This is a killer portfolio piece — "I built an ML system for Fortaleza's transit authority"

### 3.6 — API & Deployment
- Wrap the best model in a FastAPI endpoint
- Containerize with Docker
- Deploy to a free tier (Railway, Render, Fly.io)
- Endpoint: `GET /predict?line=41&date=2025-03-15&hour=8` → `{ "predicted_passengers": 127, "confidence": [98, 156] }`

---

## Final Thoughts

This project has the bones of something genuinely useful. Fortaleza's transit authority (ETUFOR) could benefit from passenger demand forecasting for route planning, fleet allocation, and schedule optimization. The thesis covered the hard part — wrangling real-world messy data and proving that ML can predict ridership patterns. The gap is in packaging: reproducibility, code quality, and presentation.

For a TCC, this was good work. To turn it into a portfolio standout or an open-source tool that other Brazilian cities could adapt, Phases 1 and 2 would get you 80% of the way there. Phase 3 is the cherry on top — the kind of thing that makes a recruiter say "this person ships."

Parabéns pelo TCC, Victor. 🎓🚌
