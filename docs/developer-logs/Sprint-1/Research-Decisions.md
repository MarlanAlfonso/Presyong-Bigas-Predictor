# Developer Log — Entry 03: Research Decisions
 
**Date:** 06-11-2026 | **Sprint:** Sprint 1 | **Status:** Completed

---

## What I Did
Conducted a literature review session to study related research (RRLs), evaluate modeling options, and finalize key research design decisions before Sprint 2 begins. Also initiated a formal data request for the pre-2018 dataset.

--- 

## Decisions Made
 
### 1. Related Literature — 8 RRLs Identified and Studied
 
The following studies were reviewed and confirmed as the core RRL set for the research paper:
 
| # | Citation | Relevance |
|---|---|---|
| 1 | Paz, G. (2017). *Forecasting the retail price of well-milled rice in the Philippines using ARIMA modeling.* DLSU. | Direct precedent — same commodity (well-milled), same PSA data source, same ARIMA methodology. Best model: ARIMA(1,1,0) on 2010–2015 data. |
| 2 | Kevin-Caldemon-Handa et al. (2023). *Forecasting value of production of palay and retail price of rice using ARIMA modelling.* WJARR, 17(3). https://doi.org/10.30574/wjarr.2023.17.3.0345 | Uses PSA OpenStat (same source). Best model: ARIMA(1,1,1) for all three rice varieties. Baseline parameter reference for Sprint 3. |
| 3 | Balilla, J., et al. (2023). *A 6-year forecast of egg, rice, and onion retail prices in the Philippines: An application of ARIMA and SARIMA models* [Preprint]. ResearchGate. | Confirms SARIMA outperforms ARIMA for rice. SARIMA(3,1,0)(0,0,1) identified as best fit — reference starting point for our grid search. Note: preprint, verify publication status before citing in paper. |
| 4 | Duyapat, C. (2025). *Forecasting Philippine rice prices: Comparison of traditional time series and machine learning models.* JMSS, 6(6), 18–28. https://doi.org/10.32996/jmss.2025.6.6.3 | Most recent and comprehensive PH study. 8 models tested head-to-head (ARIMA, SARIMA, Prophet, ETS, TBATS, Theta, RF, XGBoost) on 430 monthly observations. Random Forest achieved best accuracy; ARIMA structurally adequate but higher errors. Defines our research gap clearly. |
| 5 | Parreño, S. J. E., et al. (2023). *Forecasting quarterly rice and corn production in the Philippines: SARIMA and Holt-Winters.* ResearchGate. | Supports SARIMA applicability to Philippine agricultural data. Provides food security and policy framing for Introduction and Conclusion. |
| 6 | Taylor, S. J., & Letham, B. (2018). *Forecasting at scale.* The American Statistician, 72(1), 37–45. https://doi.org/10.1080/00031305.2017.1380080 | Original Prophet paper. Required citation whenever Prophet is used. Changepoint detection directly applicable to EO 105 and RTL structural breaks in our series. |
| 7 | Marconi, M., et al. (2021). *Comparing Prophet and deep learning to ARIMA in forecasting wholesale food prices.* Forecasting, 3(3), 644–662. https://doi.org/10.3390/forecast3030040 | Empirical evidence that ARIMA ≈ LSTM in accuracy; Prophet is easier but considerably less accurate. Justifies SARIMA as primary model, Prophet as benchmark. |
| 8 | Briones, R., & Galang, I. (2020). *Distributional impacts of the rice tariffication policy in the Philippines.* Food Policy, 98, 101935. https://doi.org/10.1016/j.foodpol.2020.101935 | Scholarly basis for the 2019 Rice Tariffication Law (RA 11203) as a structural break in our training data. Required policy context for Results and Discussion. |
 
> **Research gap confirmed:** No prior study targets NCR retail well-milled rice prices specifically using SARIMA + Prophet with a deployed public dashboard, nor covers the post-EO 105 (2025) tariff regime.
 
--- 

### 2. Geographic Scope — NCR Only (with acknowledged limitation)

**Decision:** The study will focus exclusvely on NVR (Metro Manila) retail rice prices

**Rationale:**
- NCR has the most complete and consistent data in PSA OpenStat.
- Directly relevant to urban food security — NCR is a net rice importer, making retail price forecasting more impactful for consumers.
- Keeps the scope achievable within the 24-week timeline.
- All existing RRLs are either national-level or single-region, so NCR-specific is a valid and defensible scope.

**Acknowledged limitation (to be stated in paper):** Results are not generalizable to other regions. Rice prices vary significantly by region due to proximity to production areas (e.g., Regions II, III, IV-A) and local supply chains.
 
**Future work (to be stated in paper):** Extend the model to other regions, particularly Regions III, IV-A, and major Mindanao regions (X, XI, XII), as a follow-up study.

---

### 3. Models to Try
 
**Decision:** Seven models will be evaluated and compared.
 
| Model | Type | Priority |
|---|---|---|
| ARIMA | Classical time series | Required (baseline) |
| SARIMA | Classical time series | Primary model |
| Prophet | Decomposition/additive | Benchmark |
| ETS (Exponential Smoothing) | Classical time series | Comparison |
| Random Forest | Machine learning | Comparison |
| XGBoost | Machine learning | Comparison |
| LSTM | Deep learning | Comparison |

**Important constraint noted:** With ~96 observations (2018–2025), machine learning models (Random Forest, XGBoost, LSTM) are at risk of overfitting. Duyapat (2025) used 430 observations for ML models. Our ML results should be interpreted with caution and this limitation must be stated explicitly in the paper.
 > If the FOI data request (see below) is fulfilled and extends the dataset to 2010–2025 (~180+ observations), the ML models become more viable. The full 7-model comparison will be revisited in Sprint 3 based on the final dataset size.
 
**Minimum for a publishable paper:** ARIMA + SARIMA + Prophet. The remaining four are additions if time and data permit.

---

### 4. System Architecture — NCR First, Multi-Region Later
 
**Decision:** The web application will be built for NCR only in this project cycle. Multi-region support will be integrated in a future version.
 
**Technical note already addressed in schema:** The roadmap's SQL schema already includes a `region` column in the database design. This means adding other regions later is a data ingestion task, not a system rebuild. No architectural changes will be needed.
 
**Risk flagged:** PSA data quality outside NCR is inconsistent — some regions have missing months. Multi-region feasibility will only be confirmed when the data is actually downloaded. Do not promise multi-region coverage in Paper 1.
 
---
 
### 5. PSA Data Request — 2010–2025
 
**Goal:** Obtain monthly retail rice prices for NCR from January 2010 to December 2017 to extend the current dataset (which starts at 2018) and increase the total observation count from ~96 to ~180+.
 
**Action taken:**
- Submitted a formal data request via the FOI portal at https://foi.gov.ph
- Requested: monthly retail prices of well-milled rice, regular-milled rice, and special rice in NCR, January 2010–December 2017
- Stated purpose: academic research on rice price forecasting
- By law (RA 11032), PSA must respond within 15 working days
**Pending action:**
- Follow-up email to PSA directly (info@psa.gov.ph) — to be sent in the coming days
- Also check PSA's publication archive at psa.gov.ph for older *Price Situation Reports* that may contain the 2010–2017 tables in PDF format
- Check OpenStat for any older table (without the `__2018` suffix) that may cover earlier years
**Expected timeline:** 2–4 weeks for FOI response. Sprint 1 data work will continue with the existing 2018–2025 dataset. Pre-2018 extension is treated as a stretch goal.
 
---
 
## Blockers
 
| Blocker | Root Cause | Solution | Time Lost |
|---|---|---|---|
| Pre-2018 PSA retail data not on OpenStat | `DB__2M__2018` table starts at 2018 | Submitted FOI request; follow-up email pending | None (non-blocking) |
 
---
 
## Next Steps
 
- Send follow-up email to PSA (info@psa.gov.ph) within the next few days
- Check OpenStat for older tables covering pre-2018 data
- Begin SQL schema design (Sprint 1)