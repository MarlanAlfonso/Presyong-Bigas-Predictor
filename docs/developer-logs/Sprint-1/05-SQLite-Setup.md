# Developer Log — Entry 05: SQLite Setup & Database Initialization
 
**Date:** 06-12-2026 | **Sprint:** Sprint 1 | **Status:** Completed

--- 
## What I did 

### 1. Installed SQLite 
- Downloaded `sqlite-tools-win-x64-*.zip` from https://www.sqlite.org/download.html
- Extracted to `C:\sqlite`
- Added `C:\sqlite` to Windows System PATH via Environment Variables
- Verified installation:

```
sqlite3 --version
```

### 3. Confirmed Python-SQLite Connection
 
Ran a smoke test from the project root:
 
```
python -c "from sqlalchemy import create_engine; e = create_engine('sqlite:///db/sinaing.db'); print('OK')"
```
> Output: `OK`

### 4. Reviewed `db/schema.sql`
 
- Reviewed the existing schema draft — no changes required
- Schema confirmed correct: single `rice_prices` table, UNIQUE constraint on `(date, commodity, region, source)`, three indexes, and `well_milled_ncr` convenience view

### 5. Wrote and Ran `src/etl/init_db.py`
 
- Wrote ETL initialization script that reads `db/schema.sql` and executes it against SQLite
- Script verifies table, view, and indexes after creation and prints a summary
- Ran from project root:
```
python src/etl/init_db.py
```
 
Output:
```
Database : ...\db\sinaing.db  [created]
Table    : rice_prices ✓
View     : well_milled_ncr ✓
Indexes  : ['idx_date', 'idx_commodity', 'idx_source']
Done.
```
 
---

## Environment Summary
 
| Tool | Detail |
|---|---|
| SQLite | Latest (added to PATH at `C:\sqlite`) |
| SQLAlchemy | Already installed (Sprint 0) |
| DB file | `db/sinaing.db` |
| Schema file | `db/schema.sql` |
| Init script | `src/etl/init_db.py` |

---
 
## Next Steps
 
- Write ETL script `src/etl/load_psa.py` to parse PSA CSV and INSERT into `rice_prices`
- Write unit tests for ETL pipeline (`tests/test_etl.py`)
- Execute schema against SQLite to create `sinaing.db`