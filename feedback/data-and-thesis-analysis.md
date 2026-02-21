# Data & Thesis Analysis — Pending Improvements

> Last updated: February 2026

---

## Data Quality — Current State

The `model-data/` CSVs are **clean and consistent**:
- All comma-separated, 20-column schema, 100 lines per year
- 2015: Jan–Dec (full year), 2018: Jan–Jul only, 2020: Mar–Dec only (no fake zeros)
- Holiday and holiday-eve flags correctly applied
- Cyclical encoding (`hour_sin`/`hour_cos`) consistent across all years

## Legacy Pipeline Issues (in `scripts/`, not affecting model-data)

These only matter if someone re-runs the raw data pipeline:

- **`scripts/zero_filler.py`** has `monthrange(2020, mes)` hardcoded — should be parameterized by year
- **Zero-filler doesn't respect source data range** — it will fabricate rows for months with no raw data
- **Intermediate files use mixed separators** (semicolon vs comma) — not an issue since model-data CSVs are already clean

---

## Thesis-Informed Enhancements (Future Work)

### 10-Execution Averaging
The thesis states results are "averages of 10 executions" (page 49). Notebook 05 has multi-run support but this could be made more systematic with proper reporting of mean ± std.

### "Bilhete Único" Effect
Fortaleza's integrated fare system adoption created abnormal ridership growth patterns. This domain context could be controlled for in the analysis or documented more prominently.

### Spatial Features
The thesis (Table 1, page 38) suggests adding lat/lon from raw card validation data. Could significantly improve predictions if raw data with coordinates is available.

### Top-10 Line Results from Thesis
The thesis appendix has per-line results for lines 041, 045, 003, 042, 051, 052, 024, 076, 026, 044. These could be added to `performances/` for validation against current notebook outputs.
