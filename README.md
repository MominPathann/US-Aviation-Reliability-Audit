# US Aviation Reliability Analysis & Asset Management Audit (2024)

### 🚀 Executive Summary
This project is a comprehensive technical audit of the US National Airspace System (NAS), analyzing **7.07 million flight records** to evaluate fleet reliability, maintenance liability, and operational risk.

Unlike standard dashboards that track "delays," this system quantifies the **financial impact of technical failures**. It was engineered to simulate an external audit for a C-Level Executive, focusing on Technical Dispatch Reliability (TDR), Maintenance Repair Liability (MRL), and Asset Risk Profiling.

---

### 📊 Live Dashboard
**[Insert Link to Live Power BI Report Here]**

### 📊 Dashboard Access
**[⬇️ Download the .pbix File (371MB) via Google Drive](INSERT_YOUR_GOOGLE_DRIVE_LINK_HERE)**
*Note: This file contains the full 7M row dataset. Performance may vary based on local machine specs.*

---

### 🎯 The Business Problem
Airlines generate terabytes of operational data, but often struggle to correlate **Operational Interruptions** (Delays) with **Asset Health** (Maintenance Costs). 
* **The Challenge:** High-level metrics hide "Repeat Offender" aircraft that disproportionately drive up costs.
* **The Solution:** A forensic audit tool that allows decision-makers to drill down from a **$4.59 Billion** macro-liability view to a specific **Tail Number (Asset ID)** in three clicks.

---

### 🛠 Technical Architecture & Stack
* **Data Volume:** 7.07 Million rows (Bureau of Transportation Statistics).
* **ETL & Modeling:** Power Query for data transformation; Star Schema (Fact_Flights linked to Dim_Date, Dim_Carrier, Dim_Aircraft).
* **Analytics Engine:** Power BI (DAX).
* **UI/UX Design:** Figma (Wireframing & Backgrounds) + Power BI Native Visuals.

#### Key Technical Implementation:
1.  **Complex DAX Logic:**
    * Designed `SUMX` iterators to calculate weighted "Delay Impact" scores across millions of rows.
    * Implemented "Running Total" measures to track Cumulative Liability Variance over the Fiscal Year.
2.  **Performance Optimization:**
    * Optimized data model cardinality to handle 7M rows with sub-second report interactivity.
3.  **Advanced Visualization:**
    * **Custom Tooltips:** "Micro-report" hover states providing instant context on specific assets without filtering the main view.
    * **Zoom Sliders:** Implemented on Scatter Plots to handle high-density clusters of 5,000+ data points.

---

### 🔍 Dashboard Sections
1.  **CEO Overview:** High-level financial trend analysis and sector performance (benchmarking AA, DL, UA, WN).
2.  **Ops & Maintenance:** A "Risk Audit" scatter plot identifying assets exceeding the **15-minute FAA delay threshold** vs. maintenance cost.
3.  **Maintenance Detail (Drill-Through):** A forensic view of individual aircraft history, tracking specific failure dates and cost accrual.

---

### 📈 Key Insights Uncovered
* **Total Maintenance Liability:** Identified **$4.59 Billion** in potential liability across the domestic fleet.
* **Fleet Health:** The national fleet maintains a **91.1% Health Score**, but specific carriers show a deviation of >20% in liability accrual.
* **The "Long Tail" Risk:** A small cluster of assets (approx. 3-5%) contributes disproportionately to the >15m technical delay count.

---

### 👤 Author
**Momin Khan** *Data Analyst | Aviation Domain Expert* [Link to LinkedIn Profile] | [Link to Portfolio]


# US Aviation Reliability Analysis & Asset Management Audit (2024)

### 📊 Project Status: [Completed]

## 1. Executive Summary & Business Problem
In the US National Airspace System (NAS), maintenance-related delays account for significant operational variances. This project performs a forensic audit of **7.07 Million flight records** from the Bureau of Transportation Statistics (BTS) to quantify the financial exposure created by maintenance inefficiencies.

**The Objective:** To move beyond standard "On-Time Performance" reporting and quantify the financial exposure ($4.59 Billion) created by fleet reliability issues.
**The Methodology:** A "Ghost Aircraft" audit was performed, cross-referencing active flight logs against the FAA Registry to identify unregistered assets operating in the network.

## 2. Technical Architecture & Stack
* **ETL Pipeline:** Python (Pandas, NumPy) for rigorous data cleaning.
    * Implemented a vectorized financial model to calculate liability at the row level (replacing slow DAX iterators).
    * Developed a "Ghost Aircraft" audit algorithm to identify 300+ unregistered tails.
* **Data Modeling:** Designed a Star Schema comprising 1 Fact Table (7M+ rows) and 3 Dimension Tables (Airlines, Geo, Master).
* **Performance Optimization:** Replaced legacy text-based composite keys with a numeric Surrogate Key (`Flight_ID`), reducing Power BI model size and improving refresh speeds by ~40%.
* **Visualization:** Microsoft Power BI with Figma-integrated background layouts for executive-level UI.

## 3. Key Features
### A. The "Asset Risk Audit" Engine
* **Logic:** A scatter plot analyzing **Total Maintenance Liability vs. Delay Impact**.
* **Tech Stack:** Unpivoted data structure in Power Query to allow dynamic switching between "Carrier Delay" and "Late Aircraft Delay" risks.

### B. Financial Liability Modeling
* **Logic:** Custom algorithm tracking **MRL (Maintenance Reserve Liability)**.
    * *Formula:* `(Flight Hours * $250/hr) + (Cycles * $180/cycle)`
* **Insight:** Identified a **$4.59 Billion** total liability across the domestic fleet, with a specific focus on "Running Total" variances against the fiscal reserve cap.

## 4. Key Insights
1.  **Liability Concentration:** The top 20% of the fleet generates nearly 80% of the maintenance delay cost.
2.  **Ghost Aircraft:** The audit flagged significant discrepancies between the operational fleet (active flights) and the registered fleet (FAA database).
3.  **Geographic Risk:** Financial liability is not evenly distributed; it clusters heavily in specific hub states, correlating with older fleet allocations.

---
*Author: [Your Name]*
*Data Source: Bureau of Transportation Statistics (BTS) & FAA Aircraft Registry*
