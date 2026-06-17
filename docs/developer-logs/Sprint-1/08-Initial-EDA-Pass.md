# Developer Log — Entry 08: Initial EDA Pass
 
**Date:** 06-15-2026 | **Sprint:** Sprint 1 | **Status:** Completed
 
---
 
## What I Did
 
Wrote and ran the first EDA notebook for the cleaned PSA retail rice price dataset.

### 1. Wrote `notebooks/01_eda_initial.ipynb`
 
Six sections covering the full initial EDA:
 
| Section | Content |
|---|---|
| Load Data | Reads `ncr_rice_prices_clean.csv`, enforces commodity ordering, sanity-checks shape |
| Missing-Value Heatmap | Seaborn heatmap across all 96 months × 3 commodities |
| Descriptive Statistics | Mean, median, std, min, max, CV% per commodity + annual mean table |
| Price Time Series | All three commodities plotted with structural break annotations |
| Box Plots by Year | Per-commodity annual distributions |
| Outlier Summary | Programmatic table of the 19 flagged rows |

### 2. Descriptive Statistics
 
| Commodity | n | Mean (₱/kg) | Median (₱/kg) | Std Dev | Min | Max | CV% |
|---|---|---|---|---|---|---|---|
| Well-Milled | 96 | 45.23 | 43.18 | 3.83 | 40.95 | 53.24 | 8.46 |
| Regular-Milled | 96 | 39.80 | 38.97 | 2.75 | 35.80 | 46.18 | 6.91 |
| Special | 96 | 56.08 | 55.58 | 2.56 | 52.68 | 61.46 | 4.56 |
 
Well-milled has the highest coefficient of variation (8.46%) — most volatile relative to its mean. This is relevant because it is the primary model series.

### 3. Annual Mean Prices (₱/kg)
 
| Year | Well-Milled | Regular-Milled | Special |
|---|---|---|---|
| 2018 | 44.68 | 39.01 | 56.03 |
| 2019 | 41.99 | 37.44 | 56.01 |
| 2020 | 42.06 | 37.22 | 55.45 |
| 2021 | 42.80 | 38.28 | 54.76 |
| 2022 | 43.12 | 38.98 | 52.94 |
| 2023 | 45.64 | 41.04 | 54.79 |
| 2024 | 52.76 | 45.28 | 61.06 |
| 2025 | 48.79 | 41.17 | 57.58 |
 
### 4. Missing-Value Heatmap Result
 
All 288 cells green — zero missing values across all three commodities for the full 2018–2025 range. Confirms the data spine is complete.
 
### 5. Key Observations
 
**Well-Milled (primary series)**
- Stable at ≈ ₱41–44/kg from 2018–2022, then surged from mid-2023, peaking at ₱53.24/kg (May 2024), before declining through 2025 to ₱48.08/kg (Dec 2025).
- No outlier rows flagged — the IQR fence absorbed the surge as a level shift.
**Regular-Milled**
- Declined from ≈ ₱39/kg (2018) to ≈ ₱36/kg (2019–2020) following the Rice Tariffication Law, then stabilised in the ₱38–39 range (2021–2023).
- Surged to ≈ ₱46/kg in mid-2024 (6 outlier rows: May–Oct 2024), before declining to ₱40.38/kg by Dec 2025.
**Special**
- Gradual decline from ≈ ₱57/kg (2018) to ≈ ₱53/kg (2022–early 2023), then surged to ≈ ₱61/kg through all of 2024 (13 outlier rows: Jan 2024–Jan 2025).
- Partial recovery in 2025 (₱57–60/kg range).
**Cross-commodity pattern**
- All three commodities show the same 2023–2024 surge and 2025 partial recovery — consistent with a common supply-side driver (El Niño + global rice export restrictions) rather than commodity-specific factors.
- RTL (2019) had a measurable effect on well-milled and regular-milled but minimal impact on special rice.
### 6. Blockers Encountered
 
| Blocker | Root Cause | Solution | Time Lost |
|---|---|---|---|
| `FileNotFoundError` on CSV load | Jupyter launched from `notebooks/` subdirectory; relative path `data/processed/...` resolved incorrectly | Changed `DATA_PATH` to `Path.cwd().parent / "data/processed/ncr_rice_prices_clean.csv"` | ~10 min |
| `FileNotFoundError` on `savefig` | `notebooks/figures/` directory did not exist; savefig paths were also relative to wrong root | Created `notebooks/figures/` via `mkdir`; updated savefig paths to `"figures/..."` | ~5 min |
 
---
 
## Files Committed
 
| File | Purpose |
|---|---|
| `notebooks/01_eda_initial.ipynb` | Initial EDA notebook — descriptive stats, heatmap, time series, box plots |
| `notebooks/figures/missing_value_heatmap.png` | Missing-value heatmap (all green — no nulls) |
| `notebooks/figures/price_series_all_commodities.png` | Time series plot with structural break annotations |
| `notebooks/figures/boxplot_by_year.png` | Annual price distribution by commodity |
 
---
 
## Next Steps
 
- Sprint 1 STAR log (`docs/sprint-logs/sprint-1.md`)