# US Aviation Asset Liability Engine

📊 **Deployment Status:** [Production Ready] | **Scale:** 7.07M Records

![Project Cover](assets/01_project_cover.png)

## 1. Executive Summary & Commercial Impact
In the highly regulated aviation leasing sector, missing or fragmented technical records create massive financial exposure during End-of-Life (EOL) asset transitions. 

This project executes a forensic data audit of **7.07 Million US flight records** to quantify the exact Maintenance Reserve Liability (MRL) accumulating across the domestic fleet. 

**The Strategic Output:** 
* Audited and verified **$4.59 Billion in total maintenance liability**.
* Reconciled **187 "Ghost Aircraft"** (assets flying without official registry matches), surfacing **$30 Million in hidden financial exposure**.
* Eliminated **$20 Million in "Phantom Liability"** by programmatically identifying and stripping 96,315 cancelled flights from the accrual logic.

### 🔗 Live Architecture Access
* **[📊 Execute Live Power BI Dashboard](https://app.powerbi.com/view?r=eyJrIjoiMzFmMDY5Y2MtNjM0NS00OTllLWEzNWYtNGI0NWIzODk4NWJlIiwidCI6ImRjNDliNmQyLTM1ZDQtNDM2Yi04Mzg4LWY1MThkOGRjYzNiZCJ9&pageName=a9e5773f86b8cbbaa4db)**
* **[⬇️ Download Semantic Model (.pbix - 166MB)](https://drive.google.com/file/d/19wxG6s6Yu3cAIU23FfI_M4V6Df_WePQx/view?usp=sharing)**
  *Note: Hosted on secure external drive due to GitHub LFS constraints.*

---

## 2. Technical Architecture: The Medallion Pipeline
This engine bypasses standard memory-bound analytics (Pandas), utilizing a highly optimized, multi-stage ETL pipeline to handle 11GB+ of unstructured regulatory data with zero loss of integrity.

* **Bronze Layer (Ingestion):** Raw BTS flight logs and FAA registries ingested. Handled massive blank strings and dirty mechanic entries without schema failure.
* **Silver Layer (DuckDB Vectorization):** Processed 7M+ rows using a vectorized Python/DuckDB backend. Built custom SQL CTEs to standardize tail numbers (N-prefixes) and execute complex `LEFT JOIN` anomaly detection against the FAA master registry. 
* **Gold Layer (Power BI / DAX):** Exported to SNAPPY-compressed Parquet files (reducing 350MB to 96MB). Engineered a Fact Constellation Schema utilizing surrogate integer keys (`Flight_ID`) to maximize VertiPaq compression.

![Data Model Schema](assets/05_star_schema_model.png)

---

## 3. Core Forensic Findings

### A. The "Ghost Aircraft" Reconciliation
A cross-reference delta calculation between FAA Registries and BTS Flight Logs initially returned 314 null matches. After building a custom SQL `CASE` statement to standardize N-prefix anomalies, **187 confirmed Ghost Aircraft** remained. These assets were actively accumulating wear-and-tear with zero official registry tracking.

### B. MRL Formula Optimization (Phantom Liability)
Initial legacy calculations applied the standard `$180 per cycle` cost uniformly. I re-engineered the pipeline logic to enforce a strict filter against cancelled flights, eliminating $20M in incorrectly accrued liability from the final audit.

---

## 4. UI/UX: Executive Decision Dashboard
The semantic layer was designed with strict Gestalt alignment and a maximized Data-Ink ratio for C-Suite executives.

### A. CEO-Level Executive Summary
A macro-level view of the $4.59 Billion liability. Features a dynamic DAX combo chart injecting a strategic reserve target line across the financial timeline. 
![Executive Summary](assets/02_executive_summary.png)

### B. The "Kill Zone" (Asset Risk Audit)
A dual-axis scatter plot isolating the top 1% of rogue aircraft bleeding capital through carrier-controllable delays and hardware degradation. 
![Asset Risk Audit](assets/03_asset_risk_audit.png)

### C. Granular Drill-Through (Asset Profile)
Forensic-level detail utilizing cross-filtered context to investigate specific tail numbers. Features a dense Financial Health Profile with linear bullet charts tracking run-rate costs against the Maintenance Reserve Liability (MRL) budget.
![Maintenance Detail](assets/04_maintenance_detail.png)

---
### 🔗 👤 Architect

**Momin Khan** *Aviation Asset Liability Auditor | Technical Records Architect* 
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/mominpathann/)
