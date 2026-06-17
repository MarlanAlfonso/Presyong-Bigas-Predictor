# Developer Log — Entry 06: ETL Pipeline & Database Load
 
**Date:** 06-12-2026 | **Sprint:** Sprint 1 | **Status:** Completed
 
---

## What I Did
 
Built and ran the full ETL pipeline that parses the PSA retail rice prices CSV and loads it into `sinaing.db`. Also wrote unit tests for the pipeline and fixed a pytest import path issue on Windows.
 
### 1. Wrote `src/etl/load_psa.py`
 
The script handles the PSA wide-format CSV (years as columns, months as rows) and converts it to the long format expected by the `rice_prices` table.
 
**Two core functions:**

| Function | What it does |
|---|---|
| `load_csv(csv_path)` | Reads the PSA CSV (skips 2-row title/blank header), pivots wide → long, normalises commodity names, builds `YYYY-MM-01` dates, skips blank or `..` cells |
| `insert_rows(df, db_path)` | Runs `INSERT OR IGNORE` so re-runs are safe; returns `{attempted, inserted, skipped}` summary |

**Key design decisions:**
- `INSERT OR IGNORE` instead of `INSERT OR REPLACE` — preserves existing rows on re-runs and makes the skipped count meaningful for auditing
- Missing price cells (`..`, blank, `-`) are skipped rather than inserted as NULL — keeps `price_per_kg NOT NULL` constraint clean
- Dates normalised to first-of-month (`2018-01-01`) to match the schema convention
- Script is also a CLI tool: `python src/etl/load_psa.py --csv ... --db ...`


### 2. Wrote `tests/test_etl.py`
 
22 unit tests across three test classes. All tests use a temporary SQLite database — the real `sinaing.db` is never touched.
 
| Class | Tests | What's covered |
|---|---|---|
| `TestLoadCsv` | 12 | Shape, columns, date format, commodity normalisation, price type, specific value check, unknown commodity skipped, missing price skipped |
| `TestInsertRows` | 7 | Row counts, duplicate handling, partial duplicates, empty DataFrame, `well_milled_ncr` view populated |
| `TestMaps` | 3 | All 3 commodities in map, all 12 months in map, zero-padded month values |

### 3. Fixed pytest Import Error (Windows)
 
**Blocker:** `ModuleNotFoundError: No module named 'src'` when running pytest.
 
**Root cause:** pytest does not automatically add the project root to `sys.path` on Windows when no `conftest.py` is present at the root level.
 
**Solution:** Added `conftest.py` at the project root:
 
```python
import sys
from pathlib import Path
 
sys.path.insert(0, str(Path(__file__).resolve().parent))
```
 
### 4. Ran ETL Against Real PSA Data
 
```
python src/etl/load_psa.py
```
 
Output:
```
Rows parsed from CSV : 288
Attempted            : 288
Inserted             : 288
Skipped              : 0  (duplicates / already loaded)
Done.
```
 
### 5. Confirmed Test Results
 
```
pytest tests/test_etl.py -v
```
 
Output: `22 passed`
 
---

## Load Summary
 
| Commodity | Rows Inserted |
|---|---|
| `well_milled` | 96 |
| `regular_milled` | 96 |
| `special` | 96 |
| **Total** | **288** |
 
96 rows per commodity = 12 months × 8 years (2018–2025). Matches expected observation count.
 
---
 
## Files Committed
 
| File | Purpose |
|---|---|
| `src/etl/load_psa.py` | ETL script — parses PSA CSV and INSERTs into `rice_prices` |
| `tests/test_etl.py` | 22 unit tests for the ETL pipeline |
| `conftest.py` | pytest path fix for Windows |
 
---
 
## Blockers
 
| Blocker | Root Cause | Solution | Time Lost |
|---|---|---|---|
| `ModuleNotFoundError: No module named 'src'` on pytest | pytest does not add project root to `sys.path` by default on Windows | Added `conftest.py` at project root with `sys.path.insert` | ~5 min |
 
---
 
## Next Steps
 
- Draft Project Abstract
- Data cleaning: handle missing dates, outliers, duplicates (`data/processed/ncr_rice_prices_clean.csv`)