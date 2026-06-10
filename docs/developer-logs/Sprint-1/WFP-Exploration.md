# Developer Log — Entry 02: WFP Data Exploration

**Date:** 06-10-2026
**Sprint:** Sprint 1
**Status:** Completed 

---
## What I did
Explored the WFP Vulnerability Analysis and Mapping (VAM) food prices dataset for the Philippines as a cross-validation source against PSA retail rice prices. 
- **Sources:** HDX (Humaniarian Data Exchange)
- **URL:** https://data.humdata.org/dataset/wfp-food-prices-for-philippines
- **File saved to:** `data/raw/wfp_philippines_food_prices.csv`

---
## Audit Results 
| Field | Values Found |
|---|---|
| Rice commodities | `Rice (milled, superior)`, `Rice (regular, milled)` |
| NCR region label | `National Capital Region` |
| Price type used | `Retail` |

---
## Filter Results
| Metric | Value |
|---|---|
| Filtered rows | 696 |
| Date range | 2000-01-15 → 2026-03-15 |
| Output file | `data/processed/wfp_ncr_rice_prices.csv` |

--- 
## Notes
- WFP data covers NCR retail rice prices from January 2000 to March 2026, longer range than needed (project uses 2015-2026), but the extra history is kept in raw form 
- Two rice commodity types were retained: `Rice (milled, superior)` and `Rice (regular, milled)`. When cross-validating against PSA's well-milled NCR series, `Rice (milled, superior)` is the closer match.
- WFP uses market-level spot prices, not PSA's official monthly average. Trends should align but values will not match exactly — suitable for cross-validation, not as a substitute series.
- Script committed to `src/etl/explore_wfp.py` and is reusable for future data updates.

---

## Files Comitted 
| File | Purpose |
|---|---|
| `data/raw/wfp_philippines_food_prices.csv` | Original WFP download, untouched |
| `data/processed/wfp_ncr_rice_prices.csv` | Filtered: NCR + Rice + Retail only (696 rows) |
| `src/etl/explore_wfp.py` | Repeatable filter and audit script |

---
## Next Step
- Document all sources in README