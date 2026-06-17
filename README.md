# Presyong Bigas Predictor
 
**Time Series Forecasting of Rice Prices in Metro Manila**

A machine learning project that forecasts monthly retail rice prices (well-milled, regular-milled, special) in NCR using PSA historical data.

| Field | Detail |
|---|---|
| **Duration** | 24 weeks (June 2 – November 28, 2026) |
| **Sprints** | 6 × 4 weeks |
| **Region** | NCR / Metro Manila |
| **Models** | SARIMA (primary), Prophet (benchmark), ARIMA, ETS, Random Forest, XGBoost, LSTM |
| **Target Accuracy** | RMSE < ₱2.00/kg |
| **Deployment** | Vercel (frontend) + Render (backend API) |
| **CI/CD** | GitHub Actions |

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

---
 
## Sprint Progress
 
| Sprint | Phase | Dates | Actual Date | Status |
|---|---|---|---|
| S1 | Data & Foundations | Jun 2 – Jun 27 | Jun 2 – Jun 17 | Completed early (Jun 17) |
| S2 | EDA & Decomposition | Jun 30 – Jul 25 | Jun 18 – | In Progress |
| S3 | Model Training | Jul 28 – Aug 22 | | Upcoming |
| S4 | Frontend & API | Aug 25 – Sep 19 | | Upcoming |
| S5 | CI/CD & Deployment | Sep 22 – Oct 17 | | Upcoming |
| S6 | Paper & Wrap-up | Oct 20 – Nov 28 | | Upcoming |


---
 
## Key EDA Findings (Sprint 1)
 
| Commodity | Mean (₱/kg) | CV% | Outliers Flagged |
|---|---|---|---|
| Well-Milled | 45.23 | 8.46% | 0 |
| Regular-Milled | 39.80 | 6.91% | 6 (May–Oct 2024) |
| Special | 56.08 | 4.56% | 13 (Jan 2024–Jan 2025) |
 
All three commodities show the same 2023–2024 price surge and partial 2025 recovery, consistent with El Niño and global rice export restrictions as a common supply-side driver. Well-milled has the highest volatility (CV 8.46%), confirming it as the most challenging and relevant primary model series.
 
Structural breaks annotated in the series:
- **March 2019** — Rice Tariffication Law (RA 11203) signed
- **August 2023** — Sharp price surge (El Niño + global supply pressure)
- **January 2025** — Executive Order 105 (revised rice tariff regime)

