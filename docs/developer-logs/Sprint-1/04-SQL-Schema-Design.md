# Developer Log — Entry 04: SQL Schema Design
**Date:** 06-12-2026 | **Sprint:** Sprint 1 | **Status:** Completed

---

## What I Did 
Designed and committed the SQLite database schema for the Presyong Bigas Predictor project. The schema will store monthly retail rice from PSA and WFP in a single normalized table

### 1. Schema Design Decisions 
**One table, not three** All three rice comodities (well-milled, regualar-milled, special) share identical attributes (date, price, source), so separate tables would violate 3NF and complicate cross-commodity queries. A single `rice_prices` table with a `commodity`column is the standard approach for time series price databases

**Columns defines:**

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-incremented surrogate key |
| `date` | DATE | Normalized to first of month (e.g. 2018-01-01) |
| `price_per_kg` | REAL | Retail price in PHP per kilogram |
| `commodity` | TEXT | `well_milled` / `regular_milled` / `special` |
| `region` | TEXT | Defaults to `NCR`; region column retained for future multi-region extension |
| `source` | TEXT | `PSA` or `WFP` |
| `price_type` | TEXT | Defaults to `retail`; extensible for wholesale stretch goal |

- **UNIQUE constraint on `(date, commodity, region, source)`** — prevents duplicate rows on ETL re-runs
- **Three indexes** on `date`, `commodity`, and `source` for query performance
- **`well_milled_ncr` view** — isolates the primary model series (PSA, well-miled, NCR) so notebooks and the FastAPI backend can query it without repeating filters 

### 2. Sample Data Table

| id | date | price_per_kg | commodity | region | source | price_type |
|---|---|---|---|---|---|---|
| 1 | 2018-01-01 | 43.80 | well_milled | NCR | PSA | retail |
| 2 | 2018-02-01 | 43.94 | well_milled | NCR | PSA | retail |
| 3 | 2018-01-01 | 37.26 | regular_milled | NCR | PSA | retail |
| 4 | 2018-01-01 | 54.62 | special | NCR | PSA | retail |
| 5 | 2018-01-01 | 44.10 | well_milled | NCR | WFP | retail |

### 3. File Commited 

```
db/schema.sql
```
> Schema is ready but not yet executed. Actual DB creation and CSV ingestion is scheduled for Sprint 1 (ETL pipeline)

---

## Next Steps 
- Write ETL script (`src/etl/load_psa.py`) to parse PSA CSV and INSERT into `rice_prices`
- Write unit tests for ETL pipeline (`tests/test_etl.py`)
- Execute schema against SQLite to create `sinaing.db`