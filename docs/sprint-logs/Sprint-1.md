# Sprint 1 STAR Log — Data Extraction & Foundations
 
**Sprint:** 1 of 6 | **Dates:** June 2 – June 17, 2026 | **Phase:** Phase 1 — Data & Foundations | **Status:** Completed

---

## Situation 

The Presyong Bigas Predictor project needed a clean, structured historical dataset of NCR retail rice prices before any modeling or EDA could begin. The primary source (PSA OpenStat) only goes back to 2018 (not 2015 as originally planned) reducing the dataset from ~132 to 96 monthly observations per commodity. A formal FOI request was submitted to PSA for pre-2018 data; response is pending. The project proceeded with the available 2018–2025 data (288 rows across 3 commodities), which is sufficient for SARIMA modeling. 
 
Additionally, the project name was updated from "Sinaing Predictor" to **Presyong Bigas Predictor**

---

## Task 

By end of Sprint 1, the goal was to:
 
1. Acquire and validate the PSA retail rice price dataset
2. Explore the WFP dataset as a cross-validation source
3. Design and initialize the SQLite database schema
4. Build and test the full ETL pipeline
5. Clean the dataset and produce the processed CSV
6. Run the first EDA pass on the cleaned data
7. Document all sources in the README
8. Write this STAR log

--- 

## Action 

### Data Acquisition 

- Downloaded PSA OpenStat retail rice prices for NCR, Jan 2018–Dec 2025, 3 commodities (well-milled, regular-milled, special). Saved to `data/raw/psa_retail_rice_prices_ncr_2018_2025.csv`.
- Noted data limitation: PSA OpenStat `DB__2M__2018` table starts at 2018, not 2015. Submitted FOI request via foi.gov.ph for Jan 2010–Dec 2017 data. Pre-2018 extension treated as stretch goal.
- Explored WFP VAM food prices dataset (HDX). Filtered to NCR + Rice + Retail → 696 rows, Jan 2000–Mar 2026. Saved filtered output to `data/processed/wfp_ncr_rice_prices.csv`. Noted that WFP uses market-level spot prices (not PSA official monthly averages) — suitable for cross-validation only.


### Schema & Database
- conducted literature review. Identified 8 RRLs. Confirmed research gap: no prior study targets NCR retail well-milled rice specifically using SARIMA + Prophet with a deployed dashboard covering the post-EO 105 (2025) tariff regime.
- Finalized research design decisions: NCR-only scope, 7 models to evaluate (ARIMA, SARIMA, Prophet, ETS, Random Forest, XGBoost, LSTM), minimum publishable set is ARIMA + SARIMA + Prophet.
- Designed SQLite schema (`db/schema.sql`): single `rice_prices` table, UNIQUE constraint on `(date, commodity, region, source)`, three indexes, `well_milled_ncr` convenience view.
- Installed SQLite, verified Python-SQLite connection via SQLAlchemy.
- Wrote and ran `src/etl/init_db.py` — created `db/sinaing.db`, confirmed table, view, and indexes.


### ETL Pipeline & Data Cleaning

- Wrote `src/etl/load_psa.py`: parses PSA wide-format CSV (years as columns, months as rows), pivots to long format, normalizes commodity names, builds `YYYY-MM-01` dates, uses `INSERT OR IGNORE` for idempotent re-runs. Loaded 288 rows (96 per commodity), 0 skipped.
- Wrote 22 unit tests in `tests/test_etl.py` across 3 classes: `TestLoadCsv` (12), `TestInsertRows` (7), `TestMaps` (3). All 22 passing.
- Fixed Windows pytest import error (`ModuleNotFoundError: No module named 'src'`) by adding `conftest.py` at project root with `sys.path.insert`.
- Wrote `src/etl/clean_psa.py`: three cleaning steps — missing month forward-fill (LOCF), IQR 1.5× outlier flagging per commodity, duplicate drop. Output: `data/processed/ncr_rice_prices_clean.csv` (288 rows, 8 columns including `gap_filled` and `is_outlier` flags).
  - Gaps filled: 0
  - Outliers flagged: 19 (6 regular-milled May–Oct 2024; 13 special Jan 2024–Jan 2025) — all real price movements, rows kept.
  - Duplicates dropped: 0


### Initial EDA

- Wrote and ran `notebooks/01_eda_initial.ipynb`. Six sections: data load, missing-value heatmap, descriptive statistics, price time series with structural break annotations, annual box plots, outlier summary.
- Key EDA findings:
  - Zero missing values confirmed across all 288 cells.
  - Well-milled has the highest CV (8.46%) — most volatile of the three, appropriate as primary model series.
  - All three commodities show the same 2023–2024 surge and 2025 partial recovery, consistent with El Niño + global rice export restrictions as a common supply-side driver.
  - RTL (2019) had measurable impact on well-milled and regular-milled but minimal effect on special rice.
- Two path-related blockers resolved during notebook execution (see Blockers table below).

---

## Results 

| Deliverable | Status | Evidence |
|---|---|---|
| PSA dataset acquired | Done | `data/raw/psa_retail_rice_prices_ncr_2018_2025.csv` |
| WFP dataset explored and filtered | Done | `data/processed/wfp_ncr_rice_prices.csv` (696 rows) |
| README updated with both sources | Done | `README.md` |
| SQL schema designed | Done | `db/schema.sql` |
| SQLite DB initialized | Done | `db/sinaing.db` — table, view, 3 indexes confirmed |
| ETL script written and ran | Done | `src/etl/load_psa.py` — 288 rows inserted |
| 22 unit tests passing | Done | `tests/test_etl.py` — `pytest` all green |
| Data cleaning complete | Done | `data/processed/ncr_rice_prices_clean.csv` — 288 rows, 0 nulls |
| Initial EDA complete | Done | `notebooks/01_eda_initial.ipynb` + 3 figures in `notebooks/figures/` |
| Abstract drafted | Done | Draft v1 on file — submission next year |
| Sprint 1 STAR log | Done | This file |


### Descriptive Statistics (from EDA)
 
| Commodity | n | Mean (₱/kg) | Std Dev | CV% |
|---|---|---|---|---|
| Well-Milled | 96 | 45.23 | 3.83 | 8.46 |
| Regular-Milled | 96 | 39.80 | 2.75 | 6.91 |
| Special | 96 | 56.08 | 2.56 | 4.56 |


### Blockers
 
| Blocker | Root Cause | Solution | Time Lost |
|---|---|---|---|
| `python -m venv venv` hung on ensurepip | Possible network/AV interference | Used `--without-pip` + manual `get-pip.py` bootstrap | ~20 min |
| PowerShell could not run `venv\Scripts\activate` | PS script execution policy blocks `.ps1` | Used `cmd /k "venv\Scripts\activate.bat"` | ~5 min |
| PSA retail data only available from 2018 | `DB__2M__2018` table starts at 2018 | Adjusted scope to 2018–2025; FOI request submitted for 2010–2017 | ~10 min |
| `ModuleNotFoundError: No module named 'src'` on pytest | pytest does not add project root to `sys.path` on Windows by default | Added `conftest.py` at project root with `sys.path.insert` | ~5 min |
| `FileNotFoundError` on CSV load in notebook | Jupyter launched from `notebooks/` subdirectory; relative path resolved incorrectly | Changed `DATA_PATH` to `Path.cwd().parent / "data/processed/..."` | ~10 min |
| `FileNotFoundError` on `savefig` | `notebooks/figures/` directory did not exist | Created directory; updated `savefig` paths to `"figures/..."` | ~5 min |