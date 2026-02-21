# Data & Thesis Analysis — Findings and Improvement Opportunities

> Analyzed: `undergradthesis-victormedeiros-tcc-unifor-2021.2.pdf` (81 pages) and  
> 6 CSV files from `C:\Users\Victor\Downloads\data-input-2015-2018-2020\`  
> Date: February 2026

---

## Thesis Overview (from PDF)

- **Title:** *Comparação de Ensembles para Previsão de Embarque de Passageiros de Ônibus*
- **University:** Universidade de Fortaleza (UNIFOR) — not UFC as stated in the README
- **Advisor:** Prof. Dr. Carlos Caminha
- **Approved:** December 9, 2021
- **Pages:** 80 (+ references and appendices)

The thesis focuses specifically on **ensemble comparison** (Bagging, Stacking, Boosting) for bus passenger boarding prediction. Line 041 (PARANGABA / OLIVEIRA PAIVA / PAPICU) is the primary test case — the busiest line in Fortaleza. The appendix shows results for the top 10 lines: 041, 045, 003, 042, 051, 052, 024, 076, 026, 044.

### Key Thesis Conclusions
- Stacking eGB (Stacking with XGBoost as meta-learner) consistently outperforms all other models
- XGBoost alone achieves ~22% improvement over simpler tree-based models
- Linear models (Linear Regression, Ridge) poorly capture the non-linear hourly demand patterns
- Results are **averages of 10 executions** per model (mentioned on page 49)
- The thesis notes a social phenomenon: Fortaleza's integrated fare system ("bilhete único") caused an unusual ridership increase during its adoption period, making pre-adoption data noisier

### Future Work Mentioned in Thesis (page 66)
1. Add **spatial features** (latitude/longitude from card validations) to improve models
2. Compare with **LSTM neural networks** for time-series framing
3. Apply the same feature engineering + modeling pipeline to **other domains** with similar behavioral patterns

---

## Data Files Analysis

### File Inventory

| File | Size | Rows | Separator | Columns | Unique Lines |
|------|------|------|-----------|---------|--------------|
| `data_input_nozerofill_2015.csv` | 478 MB | 1,931,193 | comma | 21 | 396 |
| `data_input_nozerofill_2018.csv` | 90 MB | 1,150,212 | comma | 11 | 390 |
| `data_input_nozerofill_2020.csv` | 112 MB | 1,420,599 | **semicolon** | 11 | 404 |
| `data_input_zerofill_2015.csv` | 161 MB | 2,081,990 | **semicolon** | 11 | 396 |
| `data_input_zerofill_2018.csv` | 95 MB | 1,229,966 | comma | 11 | 390 |
| `data_input_zerofill_2020.csv` | 123 MB | 1,604,354 | **semicolon** | 11 | 404 |

### Model-Ready CSVs (in repo, `dados-para-modelos/`)

| File | Size | Rows | Columns | Sep |
|------|------|------|---------|-----|
| `2015/top100_linhas_data_model_2015.csv` | 45 MB | 414,688 | 20 | comma |
| `2018/top100_linhas_data_model_2018.csv` | 55 MB | 511,509 | 20 | comma |
| `2020/top100_linhas_data_model.csv` | 81 MB | 756,593 | 20 | comma |

The model-ready CSVs are clean and consistent: 20 columns, comma-separated, identical schema with one-hot day-of-week and holiday flags. These are the ones actually used by the notebooks.

---

## 🔴 Data Quality Issues Found

### 1. Separator Inconsistency
Files use a random mix of comma and semicolon separators. This forces every reader to detect or hardcode the separator per file.

- 2020 nozerofill: semicolon (while 2015/2018 nozerofill use comma)
- 2015 zerofill: semicolon (while 2018 zerofill uses comma)

**Impact:** Any script loading "all years" needs per-file separator handling.

### 2. Column Schema Mismatch Across Years

The **2015 nozerofill** has 21 columns with ALL cyclical features pre-computed:
```
hora_sin, hora_cos, d_mes_sin, d_mes_cos, d_semana_sin, d_semana_cos,
d_ano_sin, d_ano_cos, mes_sin, mes_cos, semana_do_mes_sin, semana_do_mes_cos
```

The **2018/2020 nozerofill** files have only 11 columns with just `hour_sin, hour_cos`.

**And the naming differs:** 2015 uses `hora_sin`/`hora_cos`, while 2018/2020 use `hour_sin`/`hour_cos`.

### 3. 2015 Nozerofill `mes` Column Contains Line Numbers

The `mes` (month) column in the 2015 nozerofill shows values like 13, 14, 15... up to 999. These are clearly **bus line numbers leaking into the month column**. The `hora` value for midnight rows is `1` instead of `0`. This suggests the 2015 `data_builder.py` output had a column alignment bug at some point.

**The zerofill files and model-ready CSVs appear clean** — the bug only affects the nozerofill 2015 intermediate file. This doesn't impact the final results since the model-ready CSVs are correct.

### 4. Date Range Anomalies

| File | Expected Date Range | Actual Date Range |
|------|-------------------|-------------------|
| 2015 nozerofill | Jan 2015 – Dec 2015 | Jan 2015 – **Jan 12, 2016** (bleeds into next year) |
| 2018 nozerofill | Full 2018 | Jan 2018 – **Aug 2018** (only 8 months!) |
| 2018 zerofill | Full 2018 | Jan 2018 – **Jul 31, 2020** (date field says 2020!) |
| 2020 nozerofill | Full 2020 | **Mar 2020** – Jan 2, 2021 (starts in March, no Jan/Feb) |
| 2020 zerofill | Full 2020 | **Jan 2020** – Jan 2, 2021 (zero-filler added Jan/Feb with no real data) |

**Key issues:**
- **2018 data only covers Jan–Aug** — not a full year. The thesis doesn't mention this limitation clearly.
- **2020 starts in March** — the COVID lockdown in Fortaleza began mid-March 2020. January and February data is missing (not "removed due to COVID" — it was simply never collected/provided).
- **2020 zerofill fabricated Jan/Feb rows** — the zero-filler filled in January and February 2020 with zeros, even though no real data exists for those months. This means the model could learn that Jan/Feb has zero ridership, which is completely wrong.
- **2018 zerofill has dates in 2020** — the `data_hora` column contains dates up to 2020-07-31, which is clearly a bug in the zero-filler (probably hardcoded the wrong year in `monthrange(2020, mes)`).

### 5. 2020 Zero-Fill Creates False Data

Since the 2020 nozerofill only has March–December data, but the zerofill starts from January:
- ~10% of zerofill rows are zero-count (vs 3.5% for 2015)
- A large portion of those zeros are fabricated Jan/Feb rows where **the bus lines were actually operating** but no data was collected

This is a data integrity issue — the model would learn "no one rides buses in January/February" when the reality is "we have no data for those months."

---

## 💡 Improvement Opportunities

### Immediate Fixes (Phase 1 completion)

1. ~~**Fix university name in README**~~ ✅ Done — corrected to UNIFOR in all occurrences.

2. **Add `dados-para-modelos/README.md`** explaining:
   - Data source: ETUFOR (Empresa de Transporte Urbano de Fortaleza)
   - Each file contains top 100 bus lines by ridership, zero-filled, with one-hot day encoding + holiday flags
   - 2018 only covers Jan–Aug (not a full year)
   - 2020 starts from March (COVID period, no Jan/Feb data)
   - Column definitions

3. **Document the data limitations** in AGENTS.md and/or a data README:
   - 2015: Full year + 12 days of 2016
   - 2018: Only Jan–Aug
   - 2020: Only Mar–Dec (+ Jan 2021)

### Data Pipeline Fixes (Phase 1.3 / Phase 2 prep)

4. **Fix zero-filler year hardcoding** — `zero_filler.py` uses `monthrange(2020, mes)` even for 2015 data. Should be parameterized.

5. **Don't zero-fill months with no source data** — 2020 Jan/Feb should not have fabricated zero rows. The zero-filler should only fill gaps *within* the date range of existing data.

6. **Standardize separators** — All CSVs should use comma (the model-ready files already do).

7. **Standardize cyclical column naming** — Pick either `hora_sin`/`hora_cos` or `hour_sin`/`hour_cos` and use it everywhere. The model-ready CSVs use `hour_sin`/`hour_cos`, so go with that.

### Thesis-Informed Improvements (Phase 2)

8. **Add the 10-execution averaging** mentioned in the thesis — The thesis states results are "averages of 10 executions." If the notebooks currently only run once, this is a discrepancy. Add multi-run averaging with standard deviation reporting.

9. **Document the "bilhete único" effect** — The thesis notes that the integrated fare system's adoption period created abnormal ridership patterns. This is valuable domain context that should be in the data README.

10. **Spatial features** — The thesis explicitly suggests adding lat/lon as future work. The raw data contains these fields (Table 1 on page 38 shows latitude/longitude columns). If the raw CSVs still have these, this could be a Phase 3 enhancement.

11. **Copy the thesis's top-10 line results into the repo** — The appendix has per-line results for lines 041, 045, 003, 042, 051, 052, 024, 076, 026, 044. These could populate `performances/` CSVs or be referenced in the README.

---

## Summary

The data files confirm the project's legitimacy — real transit data from Fortaleza across three years. However, there are meaningful data quality issues (year mismatches in zero-filler, fabricated 2020 Jan/Feb data, 2018 only covering 8 months) that should be documented even if not fixed in the pipeline. The thesis PDF provides additional context (10-run averaging, bilhete único effect, spatial features as future work) that can enrich the repository.
