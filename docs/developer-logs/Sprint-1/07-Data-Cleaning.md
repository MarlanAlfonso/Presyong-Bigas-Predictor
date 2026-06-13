# Developer Log — Entry 07: Data Cleaning
 
**Date:** 06-13-2026 | **Sprint:** Sprint 1 | **Status:** Completed

---

## What I Did 

Wrote the data cleaning script for the PSA retail price dataset. 

### 1. Wrote `src/etl/clean_psa.py`
 
Three cleaning steps applied in order:
 
| Step | Method | Result |
|---|---|---|
| Missing months | Forward-fill (LOCF) per commodity | 0 gaps found; code is a safety net for future updates |
| Outlier detection | IQR (1.5× fence) per commodity | 19 rows flagged |
| Duplicate check | Drop on `(date, commodity, region, source)` | 0 duplicates found |

**Design decisions:**
- **Missing months → forward-fill (LOCF).** Rice prices are sticky — a missing month reflects a reporting gap, not a true price drop. Forward-fill is the standard recommendation for short gaps in official price series (Hyndman & Athanasopoulos, 2021, https://otexts.com/fpp3/missing-outliers.html).
- **Outlier detection → IQR (1.5× fence, per commodity).** The series has a known structural break (RTL 2019, EO 105 2025) and is right-skewed. Z-score assumes normality and would over-flag legitimate policy-driven spikes. IQR is distribution-free and more robust for this type of data (Rousseeuw & Hubert, 2011, https://doi.org/10.1002/widm.2).
- **Outlier handling → flag only (`is_outlier = True`), rows kept.** The 2024 price surge is real signal — removing it would teach the model to ignore future supply shocks. Flagging allows the paper to document it while preserving training data integrity (Zhang, 2003, https://doi.org/10.1016/S0925-2312(01)00702-0).


### 2. Outlier Summary
 
| Commodity | Flagged | Months | Direction | Notes |
|---|---|---|---|---|
| `well_milled` | 0 | — | — | All 96 rows within fence |
| `regular_milled` | 6 | May–Oct 2024 | HIGH | Post-RTL + El Niño price surge |
| `special` | 13 | Jan 2024–Jan 2025 | HIGH | Sustained elevated plateau |
| **Total** | **19** | | | |
 
All 19 flagged rows are real price movements, not data errors.
 
### 3. Script Output
 
```
Loaded from DB       : 288 rows
Gaps forward-filled  : 0
Outliers flagged     : 19
Duplicates dropped   : 0
Written to           : data/processed/ncr_rice_prices_clean.csv
Final row count      : 288
Done.
```

### 4. Output File Structure
 
`data/processed/ncr_rice_prices_clean.csv` — 288 rows, 8 columns:
 
| Column | Type | Notes |
|---|---|---|
| `date` | DATE | First of month (YYYY-MM-DD) |
| `price_per_kg` | REAL | PHP per kg |
| `commodity` | TEXT | `well_milled` / `regular_milled` / `special` |
| `region` | TEXT | `NCR` |
| `source` | TEXT | `PSA` |
| `price_type` | TEXT | `retail` |
| `gap_filled` | BOOL | `True` if row was forward-filled |
| `is_outlier` | BOOL | `True` if outside IQR 1.5× fence |
 
---
 
## Files Committed
 
| File | Purpose |
|---|---|
| `src/etl/clean_psa.py` | Cleaning script — missing months, outlier flagging, duplicate check |
| `data/processed/ncr_rice_prices_clean.csv` | Cleaned dataset, ready for EDA |
 
---

## Next Steps
- First EDA pass: descriptive stats, missing-value heatmap (`notebooks/01_eda_initial.ipynb`)