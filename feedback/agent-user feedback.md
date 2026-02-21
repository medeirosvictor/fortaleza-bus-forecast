# Future Improvements

> Project: Onboarding Prediction & Data Analysis for Fortaleza Bus Transit
> Last updated: February 2026

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
- 2020 data without controlling for the pandemic is misleading — ridership dropped 60–80% in many cities
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

**Goal:** Transform from a thesis project into a reusable, extensible tool.

### 3.1 — Thin Notebook Wrappers
- `src/fortaleza_bus_forecast/` package exists with `data/`, `models/`, `visualization/` modules
- **Remaining:** Notebooks still contain duplicated logic (model training loops, metric computation). Ideally they should become thin wrappers calling package functions.

### 3.2 — Experiment Tracking
- Add MLflow or Weights & Biases for experiment tracking
- Log every run: model type, hyperparameters, features used, train/test split, all metrics
- Makes it trivial to compare 100+ experiments and find the best configuration

### 3.3 — Multi-Line Modeling Strategy
- Currently: one model per bus line (scales poorly — 100+ models to maintain)
- Add experiments with:
  - **One global model** with `linha` as a feature (or embedding)
  - **Cluster-based models** — group lines by ridership volume (high/medium/low)
  - Compare per-line vs global vs clustered performance

### 3.4 — Modern ML Approaches
- Try gradient-boosted models with native categorical support (CatBoost, LightGBM categorical mode)
- Explore Prophet or NeuralProphet for the time-series framing — they handle holidays and seasonality natively
- Consider a simple LSTM or Transformer for the time-series approach

### 3.5 — Interactive Dashboard
- Build a Streamlit or Gradio app that:
  - Lets users pick a bus line, date, and hour
  - Shows the predicted passenger count with confidence interval
  - Displays historical patterns for that line

### 3.6 — API & Deployment
- Wrap the best model in a FastAPI endpoint
- Containerize with Docker
- Deploy to a free tier (Railway, Render, Fly.io)
- Endpoint: `GET /predict?line=41&date=2025-03-15&hour=8` → `{ "predicted_passengers": 127, "confidence": [98, 156] }`
