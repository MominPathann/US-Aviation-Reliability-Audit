# US Aviation Reliability Analysis & Asset Management Audit (2024)

### 📊 Project Status: [Completed]

## 1. Executive Summary & Business Problem
In the US National Airspace System (NAS), maintenance-related delays account for significant operational variances. This project simulates an external forensic audit of **7.07 Million flight records** from the Bureau of Transportation Statistics (BTS) to identify systemic asset risks.

**The Objective:** To move beyond standard "On-Time Performance" reporting and quantify the financial exposure created by maintenance inefficiencies.
**The Scope:** Analysis of **$4.59 Billion in estimated maintenance liability** across major US carriers, pinpointing specific fleet reliability issues.

![Project Cover](assets/01_project_cover.jpg)

### 🔗 Dashboard Access
* **[📊 View Live Power BI Report](INSERT_YOUR_PUBLISHED_LINK_HERE)**
* **[⬇️ Download .pbix File (371MB)](INSERT_YOUR_GOOGLE_DRIVE_LINK_HERE)**
    * *Note: Hosted on Google Drive due to GitHub file size limits.*

---

## 2. Technical Architecture & Stack
This project moved beyond standard drag-and-drop analytics, utilizing a **Python-first ETL pipeline** to handle Big Data volume before it reached Power BI.

* **ETL Pipeline:** Python (Pandas, NumPy) for rigorous data cleaning.
    * **Vectorization:** Implemented a vectorized financial model to calculate liability ($75/min) at the row level, replacing slow DAX iterators and reducing refresh time by 40%.
    * **Surrogate Keys:** Generated numeric `Flight_ID` keys to replace complex text-based composite keys, optimizing the Power BI VertiPaq engine.
* **Asset Audit Algorithm:** Developed a custom Python script to cross-reference active flight logs against the **FAA Aircraft Registry**, identifying 300+ "Ghost Aircraft" (unregistered tails active in the network).
* **Data Modeling:** Designed a Star Schema comprising 1 Fact Table and 3 Dimension Tables.

### Data Model Schema
The model uses a Star Schema to optimize performance for 7M+ rows.
![Data Model Schema](assets/05_star_schema_model.png)

---

## 3. Key Features & Visuals

### A. CEO-Level Executive Summary
A high-level view of the $4.59 Billion liability, tracking Technical Dispatch Reliability (TDR) and On-Time Performance (80%) against a custom fiscal reserve cap.
![Executive Summary](assets/02_executive_summary.png)

### B. The "Asset Risk Audit" Engine
A custom scatter plot analyzing **Total Maintenance Liability vs. Delay Impact**. This visual instantly segments the fleet to identify "High Cost / High Delay" outliers (Red Quadrant) versus healthy assets.
* **Tech Stack:** Used Power Query to unpivot delay columns (`CarrierDelay`, `LateAircraftDelay`), enabling dynamic risk switching.
![Asset Risk Audit](assets/03_asset_risk_audit.png)

### C. Granular Drill-Through
Forensic-level detail allowing stakeholders to investigate specific tail numbers (e.g., N17347), analyzing their specific run-rate cost against the Maintenance Reserve Liability (MRL) budget.
![Maintenance Detail](assets/04_maintenance_detail.png)

---

## 4. Key Insights Uncovered
1.  **Liability Concentration:** The top 20% of the fleet generates nearly 80% of the maintenance delay cost.
2.  **Ghost Aircraft:** The audit flagged significant discrepancies between the operational fleet (active flights) and the registered fleet (FAA database), indicating potential data governance gaps.
3.  **Geographic Risk:** Financial liability is not evenly distributed; it clusters heavily in specific hub states, correlating with older fleet allocations.

---
*Author: Momin Khan | Data Analyst & Aviation Domain Expert*
*Data Source: Bureau of Transportation Statistics (BTS) & FAA Aircraft Registry*
