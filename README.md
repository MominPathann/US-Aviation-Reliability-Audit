# US Aviation Reliability Analysis & Asset Management Audit (2024)

### 🚀 Executive Summary
This project is a comprehensive technical audit of the US National Airspace System (NAS), analyzing **7.07 million flight records** to evaluate fleet reliability, maintenance liability, and operational risk.

Unlike standard dashboards that track "delays," this system quantifies the **financial impact of technical failures**. It was engineered to simulate an external audit for a C-Level Executive, focusing on Technical Dispatch Reliability (TDR), Maintenance Repair Liability (MRL), and Asset Risk Profiling.

---

### 📊 Live Dashboard
**[Insert Link to Live Power BI Report Here]**

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
