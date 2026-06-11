# "Sinaing" Predictor
 
**Time Series Forecasting of Rice Prices in Metro Manila**

--- 

## Data Sources 

### Primary Dataset — PSA OpenStat Retail Prices
 
| Field | Detail |
|---|---|
| **Portal** | PSA OpenStat |
| **Table** | Cereals: Retail Prices of Agricultural Commodities by Geolocation, Commodity, Year and Period |
| **URL** | https://openstat.psa.gov.ph/PXWeb/pxweb/en/DB/DB__2M__2018/0042M4ARA01.px/table/tableViewLayout1/ |
| **Region** | NCR / Metro Manila |
| **Commodities** | Rice, Well-Milled (1kg) · Rice, Regular-Milled (1kg) · Rice, Special (1kg) |
| **Date Range** | January 2018 – December 2025 |
| **Observations** | ~96 monthly records |
| **Price Type** | Retail |
| **File** | `data/raw/psa_retail_rice_prices_ncr_2018_2025.csv` |

> **Data Limitation:** PSA OpenStat retail prices begin at 2018, not 2015 as originally planned. The pre-2018 gap is documented as a limitation in the research paper. The reduced dataset (~96 obeservations) remains sufficient for SARIMA modeling. 

### Cross-Validation Dataset — WFP VAM Food Prices

| Field | Detail |
|---|---|
| **Portal** | Humanitarian Data Exchange (HDX) |
| **Dataset** | WFP Food Prices for Philippines |
| **URL** | https://data.humdata.org/dataset/wfp-food-prices-for-philippines |
| **Region** | National Capital Region |
| **Commodities** | Rice (milled, superior) · Rice (regular, milled) |
| **Date Range** | January 2000 – March 2026 |
| **Observations** | 696 rows (NCR + Rice + Retail filtered) |
| **Price Type** | Retail (market-level spot prices) |
| **Files** | `data/raw/wfp_philippines_food_prices.csv` (raw) · `data/processed/wfp_ncr_rice_prices.csv` (filtered) |

> **Usage note:** WFP uses market-level spot prices; PSA uses official monthly averages. Trends should align but values will not match exactly. WFP data is used for cross-validation only, not as substitute series. When comparing against PSA's well-milled series, `Rice (milled, superior)` is the closer match.
