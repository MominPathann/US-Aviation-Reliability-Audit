# US Aviation Reliability Analysis & Asset Risk Audit (2024)

**📊 Status:** Production Ready &nbsp;|&nbsp; **Scale:** 7.07M Records &nbsp;|&nbsp; **Region:** US Domestic &nbsp;|&nbsp; **Analyst:** Momin Khan

![Project Cover](assets/01_project_cover.png)

---

## The Problem

Airlines and MRO operators routinely make capital allocation decisions based on maintenance liability data that is never audited at the record level. Cancelled flights get counted as completed cycles. Ghost aircraft accumulate wear with no registry tracking. The result is a financial model built on dirty data — and no one knows by how much.

This project forensically audits **7.07 million BTS flight records** against the FAA Master Registry to answer one question: *what is the actual, verified maintenance liability of the US domestic fleet?*

### 🔗 Live Access
- **[📊 Execute Live Power BI Dashboard](https://app.powerbi.com/view?r=eyJrIjoiMGQwODlmZTMtZDhhZC00OTdiLTkwMzEtMzU2NmI1MTIzNGM5IiwidCI6ImRjNDliNmQyLTM1ZDQtNDM2Yi04Mzg4LWY1MThkOGRjYzNiZCJ9&pageName=a9e5773f86b8cbbaa4db)**
- **[⬇️ Download Semantic Model (.pbix — 166MB)](https://drive.google.com/file/d/1Jn2ic9zBBKTeIszjdn6WQqqnmo916Mdr/view?usp=drive_link)**
  *(Hosted externally due to GitHub LFS constraints)*

---

## Key Findings

| Finding | Result |
|---|---|
| Total Maintenance Reserve Liability (MRL) | **$4.59 Billion** |
| Total Delay Cost | **$8.30 Billion** |
| Unique Aircraft Tracked | **6,113** |
| Carriers Audited | **15** |
| Airports in Network | **348** |
| At-Risk Assets (Kill Zone) | **1,000+** |
| Ghost Aircraft Confirmed | **199** |
| Phantom Liability Eliminated | **$17.3 Million** |
| Technical Dispatch Reliability (TDR) Score | **88.7%** |
| Fleet On-Time Performance | **80.0%** |

---

## Forensic Findings

### 1. The $17.3M Phantom Liability Catch

The standard MRL formula applies a `$180 per cycle` charge to every flight record uniformly. Initial processing revealed **96,315 cancelled flights** incorrectly included in the accrual logic — generating **$17,336,700 in phantom maintenance liability** that never existed.

The pipeline enforces a hard-zero on cancelled flights and null AirTime records upstream in the Silver layer, before any cost calculation runs. The corrected $4.59B figure is what remains after this filter.

> *This is the difference between a dashboard and a forensic audit.*

---

### 2. The Ghost Aircraft Reconciliation

Cross-referencing BTS flight logs against the FAA Master Registry initially produced **314 null matches** — aircraft flying with no official record. The root cause: inconsistent N-prefix formatting across the two datasets. After applying tail number standardization on both sides:

**314 raw nulls → 115 resolved by standardization → 199 confirmed Ghost Aircraft**

These 199 assets were actively accumulating flight hours and cycles with zero official registry tracking — creating unquantified liability exposure for any operator holding them on lease.

---

### 3. Liability Concentration

The top 20% of the fleet generates approximately 80% of all maintenance delay cost. Generalized fleet upgrades are a capital misallocation. The Kill Zone view isolates the exact tail numbers requiring immediate intervention.

---

### 4. Geographic Liability Clustering

Maintenance liability concentrates in legacy hub states — Texas ($1.02B), Florida ($885M), California ($757M) — independently of raw flight volume. This points to station-level maintenance culture and infrastructure age, not purely operational scale.

---

## Technical Architecture: The Medallion Pipeline

Built to handle **11GB+ of unstructured regulatory data** without memory failure or schema collapse.

```
RAW BTS + FAA DATA  (12 monthly ZIPs + MASTER.txt + ACFTREF.txt)
         │
         ▼
┌─────────────────────┐
│   BRONZE LAYER      │  Monthly BTS ZIPs downloaded with retry logic.
│   download_and_     │  CSVs extracted. Dirty strings, blank entries,
│   extract()         │  and malformed tail numbers ingested without
└─────────────────────┘  schema failure.
         │
         ▼
┌─────────────────────┐
│   SILVER LAYER      │  DuckDB vectorized ETL on 7.07M rows.
│   run_silver_       │  N-prefix tail standardization. Corrected MRL
│   pipeline()        │  formula (cancelled flights hard-zeroed).
└─────────────────────┘  Star schema extracted: 2 fact tables,
                         3 dimension tables. SNAPPY Parquet export.
         │
         ▼
┌─────────────────────┐
│   AUDIT LAYER       │  Python set difference: active_fleet − registered.
│   run_ghost_        │  FAA MASTER.txt + ACFTREF.txt merged for enriched
│   aircraft_audit()  │  aircraft profiles. 199 ghost aircraft confirmed.
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   GOLD LAYER        │  6x SNAPPY-compressed Parquet files.
│   Power BI / DAX    │  Fact Constellation Schema. Dynamic DAX risk
└─────────────────────┘  threshold parameters for executive simulation.
```

**Why DuckDB over Pandas:**
A 7M-row dataset loaded into a Pandas DataFrame requires 16GB+ RAM and crashes standard machines. DuckDB's columnar vectorized engine uses SIMD (Single Instruction, Multiple Data) — processing data in memory-efficient chunks, executing aggregates across thousands of values per CPU clock cycle, then discarding the raw chunk before loading the next. Sub-second query speeds. Zero memory overflow.

---

## Output Schema

Six SNAPPY-compressed Parquet files exported to `/data_processed/`:

| File | Rows | Columns | Description |
|---|---|---|---|
| `Aviation_Fact_Table.parquet` | 7,079,061 | 15 | Core flight metrics, MRL liability, delay cost |
| `Aviation_Fact_Delay_Table.parquet` | 2,354,307 | 3 | Unpivoted delay cause breakdown (flights with delays only) |
| `Aviation_Airlines_Dim.parquet` | 15 | 3 | Carrier codes and DOT/IATA identifiers |
| `Aviation_Geo_Dim.parquet` | 348 | 3 | Airport codes, cities, and states |
| `Master_Dim.parquet` | 5,913 | 6 | FAA registry: aircraft type, manufacturer, model, seat count |
| `Ghost_Aircraft_Audit.parquet` | 199 | 1 | Unregistered tail numbers confirmed flying in 2024 |

**Schema: Fact Constellation (2 Fact Tables, 3 Dimension Tables)**

```
Aviation_Fact_Table ──────────────────── Aviation_Airlines_Dim
        │                                  (Reporting_Airline)
        │ Flight_ID ────────────────────── Aviation_Fact_Delay_Table
        │                                  (Flight_ID → Delay Type, Minutes)
        │ Tail_Number ──────────────────── Master_Dim
        │                                  (N-NUMBER → MFR, MODEL, SEATS)
        │ Origin / Dest ─────────────────── Aviation_Geo_Dim
                                           (AirportCode → City, State)
```

---

## The Pipeline in Code

Four core snippets from `main_pipeline.py` that drove the key findings.

---

### 1. Corrected MRL Formula — $17.3M Phantom Liability Eliminated

Standard industry logic applies `$180` to every record including cancelled flights. This pipeline enforces a hard-zero upstream before any cost calculation runs.

```sql
-- Silver Layer: run_silver_pipeline() — DuckDB SQL
-- MRL Formula: (AirTime / 60 × $250) + $180 per cycle
-- Cancelled flights and null AirTime → hard-zeroed before calculation

CASE
    WHEN TRY_CAST(Cancelled AS INTEGER) = 1
      OR TRY_CAST(AirTime   AS INTEGER) IS NULL THEN 0.0
    ELSE ((TRY_CAST(AirTime AS INTEGER) / 60.0) * 250.0) + 180.0
END AS MRL_Liability
```

> 96,315 cancelled flights × $180 = **$17,336,700 eliminated at source.**

---

### 2. Tail Number Standardization — Ghost Aircraft Root Cause Fix

FAA registry and BTS logs use inconsistent N-prefix formatting. A raw comparison produces 314 false ghost matches. This CASE statement forces consistency before any cross-dataset join runs.

```sql
-- Silver Layer: run_silver_pipeline() — DuckDB SQL
-- Forces N-prefix on all tail numbers before FAA registry comparison
-- Without this: 314 null matches. After: 199 confirmed ghost aircraft.

CASE
    WHEN Tail_Number IS NULL OR TRIM(Tail_Number) = '' THEN 'UNKNOWN'
    WHEN TRIM(Tail_Number) NOT LIKE 'N%%' THEN 'N' || TRIM(Tail_Number)
    ELSE TRIM(Tail_Number)
END AS Tail_Number
```

> 314 raw nulls → 115 resolved by standardization → **199 genuine Ghost Aircraft confirmed.**

---

### 3. Ghost Aircraft Detection — Set Difference Audit

Tail numbers flying in BTS data with no FAA registry match. Functionally equivalent to `LEFT JOIN WHERE NULL` — implemented as Python set arithmetic against the merged FAA MASTER + ACFTREF registry.

```python
# Audit Layer: run_ghost_aircraft_audit()
# active_fleet = all tail numbers in 7.07M BTS flight records
# registered   = all tail numbers in merged FAA MASTER + ACFTREF
# orphans      = flying aircraft with zero registry match

active_fleet = set(fact_tails['Tail_Number'].dropna().apply(clean_tail))
registered   = set(merged_master['N-NUMBER_CLEAN'].dropna())

orphans = active_fleet - registered
# Output: 199 confirmed Ghost Aircraft → Ghost_Aircraft_Audit.parquet
```

---

### 4. Unpivoted Delay Fact Table — Power BI Optimized

Delay cause columns unpivoted into a long-format fact table for clean DAX aggregation. Only records with actual delay minutes included.

```sql
-- Silver Layer: run_silver_pipeline() — DuckDB SQL
-- Transforms 5 delay cause columns into 2,354,307 rows
-- Enables simple SUM(Minutes) by Delay Type in Power BI

WITH unpivoted_delays AS (
    UNPIVOT bts_flights
    ON CarrierDelay AS 'Carrier Delay',
       WeatherDelay AS 'Weather Delay',
       NASDelay AS 'NAS Delay',
       SecurityDelay AS 'Security Delay',
       LateAircraftDelay AS 'Late Aircraft Delay'
    INTO NAME "Delay Type" VALUE "Minutes"
)
SELECT Flight_ID, "Delay Type", TRY_CAST("Minutes" AS INTEGER) AS "Minutes"
FROM unpivoted_delays
WHERE "Minutes" > 0
```

---

## Repository Structure

```
aviation-reliability-audit/
│
├── README.md                        ← This file
├── requirements.txt                 ← pip install -r requirements.txt
├── .gitignore                       ← Excludes data_raw/, data_processed/
│
├── main_pipeline.py                 ← Full Medallion ETL pipeline
│
├── assets/                          ← Dashboard screenshots
│   ├── 01_project_cover.png
│   ├── 02_executive_summary.png
│   ├── 03_asset_risk_audit.png
│   ├── 04_maintenance_detail.png
│   └── 05_star_schema_model.png
│
├── data_raw/                        ← Raw source files (gitignored)
│   ├── flights_2024_*.zip           ← Monthly BTS On-Time Performance ZIPs
│   ├── MASTER.txt                   ← FAA Aircraft Registry
│   └── ACFTREF.txt                  ← FAA Aircraft Reference (type, seats)
│
└── data_processed/                  ← Pipeline outputs (gitignored)
    ├── Aviation_Fact_Table.parquet
    ├── Aviation_Fact_Delay_Table.parquet
    ├── Aviation_Airlines_Dim.parquet
    ├── Aviation_Geo_Dim.parquet
    ├── Master_Dim.parquet
    └── Ghost_Aircraft_Audit.parquet
```

---

## How to Run

```bash
# 1. Clone the repository
git clone https://github.com/mominpathann/aviation-reliability-audit.git
cd aviation-reliability-audit

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place FAA registry files in data_raw/
#    Download: https://registry.faa.gov/database/ReleasableAircraft.zip
#    Extract MASTER.txt and ACFTREF.txt into data_raw/

# 4. Run the pipeline
python main_pipeline.py

# Note: BTS data download is commented out by default.
# To download 12 months of raw BTS flight data, uncomment in __main__:
# download_and_extract()
```

**Expected outputs in `/data_processed/`:**

| File | Rows | Description |
|---|---|---|
| `Aviation_Fact_Table.parquet` | 7,079,061 | Core flight data with MRL and delay cost |
| `Aviation_Fact_Delay_Table.parquet` | 2,354,307 | Delay cause breakdown per flight |
| `Aviation_Airlines_Dim.parquet` | 15 | Carrier reference |
| `Aviation_Geo_Dim.parquet` | 348 | Airport reference |
| `Master_Dim.parquet` | 5,913 | Matched FAA aircraft registry |
| `Ghost_Aircraft_Audit.parquet` | 199 | Unregistered tail numbers |

---

## Dashboard Pages

### CEO Executive Overview
Macro-level view of the $4.59B liability. Dynamic DAX combo chart with strategic reserve target line across the financial timeline. Carrier sector breakdown by total delay cost.

![Executive Summary](assets/02_executive_summary.png)

### Ops & Maintenance — The Kill Zone
Dual-axis scatter plot: Total Maintenance Liability (X) vs. Delay Impact (Y). The red quadrant isolates the top 1% of assets exceeding both thresholds simultaneously. Parametric risk slider adjusts the threshold in real time.

![Asset Risk Audit](assets/03_asset_risk_audit.png)

### Maintenance Detail — Asset Profile Drill-Through
Forensic drill-through to individual tail number level. Displays MRL accrual, remaining budget, liability variance against fleet average, and a full 12-month cost vs. delay trend.

![Maintenance Detail](assets/04_maintenance_detail.png)

---

## Stack

`Python` &nbsp;`DuckDB` &nbsp;`SQL` &nbsp;`Pandas` &nbsp;`Apache Parquet` &nbsp;`Power BI` &nbsp;`DAX` &nbsp;`Power Query (M)` &nbsp;`FAA Registry` &nbsp;`BTS Flight Data`

---

## About

**Momin Khan** — Data Analyst | Aviation Reliability & Asset Management

Aeronautics graduate with hands-on CAR-147 maintenance experience. Background in aircraft technical records and fleet operations. Focused on the intersection of physical aviation knowledge and enterprise data architecture.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/mominpathann/)
