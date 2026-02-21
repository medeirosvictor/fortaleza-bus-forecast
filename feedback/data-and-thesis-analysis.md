# Data & Thesis Analysis — Pending Improvements

> Last updated: February 2026

---

## Data Quality Issues (documented but not fixed in pipeline)

### 1. Separator Inconsistency in Intermediate Files
Files use a mix of comma and semicolon separators (2020 nozerofill: semicolon; 2015 zerofill: semicolon; others: comma). The model-ready CSVs in `model-data/` are all comma-separated and consistent — this only affects the intermediate pipeline files.

### 2. Column Naming in Intermediate Files
2015 nozerofill uses `hora_sin`/`hora_cos`, while 2018/2020 use `hour_sin`/`hour_cos`. Model-ready CSVs are standardized to `hour_sin`/`hour_cos`.

### 3. 2020 Zero-Fill Creates False Data
The 2020 nozerofill only has March–December data, but the zero-filler added January/February rows as zeros. Those buses were actually operating — no data was collected for those months. The model could incorrectly learn "no one rides buses in January/February."

---

## Pending Pipeline Fixes

### Fix zero-filler year hardcoding
`zero_filler.py` uses `monthrange(2020, mes)` even for 2015 data. Should be parameterized by year.

### Don't zero-fill months with no source data
The zero-filler should only fill gaps *within* the date range of existing data, not fabricate rows for months where no raw data exists.

### Standardize separators
All intermediate CSVs should use comma (the model-ready files already do).

---

## Thesis-Informed Enhancements (Future Work)

### 10-Execution Averaging
The thesis states results are "averages of 10 executions" (page 49). If the notebooks currently only run once, this is a discrepancy. Add multi-run averaging with standard deviation reporting.

### "Bilhete Único" Effect
The thesis notes that Fortaleza's integrated fare system adoption created abnormal ridership patterns. This domain context could be documented more prominently or controlled for in the analysis.

### Spatial Features
The thesis explicitly suggests adding lat/lon as future work. The raw data contains latitude/longitude columns (Table 1, page 38). Could be a significant enhancement.

### Top-10 Line Results from Thesis
The thesis appendix has per-line results for lines 041, 045, 003, 042, 051, 052, 024, 076, 026, 044. These could populate `performances/` CSVs or be referenced in the README for validation.
