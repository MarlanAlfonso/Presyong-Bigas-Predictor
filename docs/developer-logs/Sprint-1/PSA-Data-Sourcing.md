# Developer Log — Entry 01: PSA Data Sourcing

**Date:** 06-05-2026
**Sprint:** Sprint 1
**Status:** Completed

---

## What I Did

### 1. Located the PSA OpenStat Retail Prices Dataset

- Navigated to the PSA Openstat portal and identified the correct table for retail rice prices: 
- **URL:**
```
https://openstat.psa.gov.ph/PXWeb/pxweb/en/DB/DB__2M__2018/0042M4ARA01.px/table/tableViewLayout1/
```
- **Table name:** Cereals: Retail Prices of Agricultural Commodities by Geolocation, Commodity, Year and Period 

### 2. Selected Filters
- Applied the following filters on the PSA Openstat table before downloading: 
| Filter | Selection |
|---|---|
| Geolocation | NCR / Metro Manila |
| Commodity | Rice, Well Milled Rice, 1kg |
| Commodity | Rice, Regular-milled, 1kg |
| Commodity | Rice, Special, 1kg |
| Year | 2018 – 2025 |
| Period | January – December |

> **Note:** Well-milled rice (1kg) is the primary series per the project roadmap. Regular-milled and Special are included for potential cross-validation.

### 3. Confirmed File Naming Convention 
- Downloaded CSV to be save as: 
```
psa_retail_rice_prices_ncr_2018_2025.csv
```
- Saved to: `/data/raw/`

### 4. Investigated Wholesale Prices Dataset
- Also checked the wholesale prices table for future reference: 
- **URL:**
```
https://openstat.psa.gov.ph/PXWeb/pxweb/en/DB/DB__2M__NWS/0052M4AWA01.px/
```

| Dataset | Year Range | Price Type |
|---|---|---|
| Retail prices | 2018 – 2025 | Retail (primary) |
| Wholesale prices | 2010 – 2025 | Wholesale (stretch goal) |

---

## Data Limitation Noted
> The original roadmap assumed data availability from 2015-2026. PSA Opestat retail prices only go back to 2018, reducing the dataset from ~132 to ~96 monthly observations. 

- **Decision:** Proceed with 2018-2025 retail data (~96 observations). This is acceptable for SARIMA modeling. The pre-2018 gap will be documented as a data limitation in the research paper. 
- **Stretch goal logged:** Incorporate wholesale price series (2010-2015) for cross-validation or dual forecasting if time permits in later sprints. 

---

## Blockers
| Blocker | Root Cause | Solution | Time Lost |
|---|---|---|---|
| Retail prices only available from 2018 | PSA OpenStat DB__2M__2018 table starts at 2018 | Adjusted dataset scope to 2018–2025; noted as data limitation | ~10 min |

--- 

## Next Step
- Exploring WFP Economic Explorer