"""
================================================================================
 US AVIATION RELIABILITY & ASSET RISK PIPELINE — FY2024
================================================================================
 Author      : Momin Khan | Data Analyst | Aviation Reliability & Asset Management
 Data Sources: Bureau of Transportation Statistics (BTS)
               FAA Aircraft Registry (MASTER.txt)
 Scale       : 7.07M Records | US Domestic Network | FY2024
 Output      : 4x SNAPPY-Compressed Parquet files → /data_processed/
--------------------------------------------------------------------------------
 PIPELINE ARCHITECTURE (Medallion Pattern):
   BRONZE  →  Raw BTS ingestion (monthly ZIPs, dirty CSVs)
   SILVER  →  DuckDB vectorized ETL (MRL formula, tail standardization)
   AUDIT   →  Ghost Aircraft reconciliation (FAA registry delta)
   GOLD    →  Compressed Parquet export → Power BI semantic layer
================================================================================
"""

import os
import time
import glob
import zipfile
import requests
import urllib3
import duckdb
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ==============================================================================
# SECTION 1: CONFIGURATION (Environment-Agnostic)
# ==============================================================================

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback for Jupyter Notebook execution
    BASE_DIR = os.getcwd()

DATA_RAW       = os.path.join(BASE_DIR, 'data_raw')
DATA_PROCESSED = os.path.join(BASE_DIR, 'data_processed')

os.makedirs(DATA_RAW, exist_ok=True)
os.makedirs(DATA_PROCESSED, exist_ok=True)

YEAR   = int(os.getenv('YEAR', 2024))
MONTHS = range(1, 13)


# ── Shared Utility ─────────────────────────────────────────────────────────────

def clean_tail(val):
    """Force N-prefix for consistent cross-dataset comparison.
    Mirrors the CASE logic applied in the Silver layer DuckDB SQL.
    Used by the Ghost Aircraft audit to standardize FAA registry keys.
    """
    if pd.isna(val):
        return None
    s = str(val).strip().upper()
    return s if s.startswith('N') else f'N{s}'


# ==============================================================================
# SECTION 2: BRONZE LAYER — BTS INGESTION
# ==============================================================================

def download_and_extract():
    """
    Downloads monthly BTS On-Time Performance ZIPs with retry logic
    and extracts raw CSVs for Silver layer processing.

    Source: Bureau of Transportation Statistics
    URL:    https://www.transtats.bts.gov/
    """
    base_url = (
        "https://transtats.bts.gov/PREZIP/"
        "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{}_{}.zip"
    )

    print(f"\n{'='*64}")
    print(f"  [BRONZE] BTS Ingestion — FY{YEAR}")
    print(f"{'='*64}")

    for month in MONTHS:
        zip_path = os.path.join(DATA_RAW, f"flights_{YEAR}_{month}.zip")

        if os.path.exists(zip_path):
            print(f"  ✓ {month:02d}/{YEAR} — Already downloaded. Skipping.")
            continue

        print(f"  ↓ Downloading {month:02d}/{YEAR}...", end=" ", flush=True)
        for attempt in range(3):
            try:
                time.sleep(2)
                r = requests.get(
                    base_url.format(YEAR, month),
                    verify=False, stream=True, timeout=60
                )
                if r.status_code == 200:
                    with open(zip_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            f.write(chunk)
                    print("Success.")
                    break
            except Exception:
                time.sleep(5)
        else:
            print("Failed after 3 attempts.")

    # Extract CSVs from all downloaded ZIPs
    print("\n  Extracting CSVs from ZIPs...")
    for z in glob.glob(os.path.join(DATA_RAW, "*.zip")):
        with zipfile.ZipFile(z, 'r') as zf:
            for csv_name in [f for f in zf.namelist() if f.endswith('.csv')]:
                target = os.path.join(DATA_RAW, csv_name)
                if not os.path.exists(target):
                    print(f"  → Extracting: {csv_name}")
                    zf.extract(csv_name, DATA_RAW)

    print("  [BRONZE] Ingestion complete.\n")


# ==============================================================================
# SECTION 3: SILVER LAYER — DUCKDB VECTORIZED ETL & FINANCIAL MODELING
# ==============================================================================

def run_silver_pipeline():
    """
    Vectorized ETL processing of 7.07M records using DuckDB.

    WHY DUCKDB OVER PANDAS:
    A 7M-row dataset loaded into a Pandas DataFrame requires 16GB+ RAM and
    crashes standard machines. DuckDB's columnar vectorized engine (SIMD)
    processes data in memory-efficient chunks — aggregating millions of rows
    per CPU clock cycle without loading the full dataset into RAM.

    KEY OPERATIONS:
    1. N-prefix tail number standardization  → prevents ghost aircraft mismatches
    2. Corrected MRL formula                 → eliminates $17.3M phantom liability
    3. Surrogate key generation (Flight_ID)  → maximizes VertiPaq compression
    4. SNAPPY Parquet export (350MB → 96MB)  → production-grade output

    OUTPUTS:
    - data_processed/Aviation_Fact_Table.parquet
    - data_processed/Master_Dim.parquet (if FAA_Registry_Master.parquet exists)
    """
    print(f"{'='*64}")
    print(f"  [SILVER] DuckDB Vectorized Pipeline")
    print(f"{'='*64}")

    con = duckdb.connect(':memory:')
    try:
        # ── Build Fact Table View ──────────────────────────────────────────────
        print("  → Building Fact Table view (7.07M records)...")
        con.execute(f"""
            CREATE OR REPLACE VIEW bts_flights AS
            SELECT
                -- Surrogate Key: Sequential integer maximizes VertiPaq compression in Power BI
                row_number() OVER () AS Flight_ID,
                CAST(FlightDate AS DATE) AS FlightDate,

                -- -----------------------------------------------------------
                -- TAIL NUMBER STANDARDIZATION
                -- Problem: FAA registry uses 'N' prefix; BTS logs inconsistent.
                -- A raw join produces 314 null matches (ghost aircraft false positives).
                -- Solution: Force N-prefix on all records before any join operation.
                -- Result: 314 raw nulls → 187 confirmed ghost aircraft remaining.
                -- -----------------------------------------------------------
                CASE
                    WHEN Tail_Number IS NULL OR TRIM(Tail_Number) = '' THEN 'UNKNOWN'
                    WHEN TRIM(Tail_Number) NOT LIKE 'N%%' THEN 'N' || TRIM(Tail_Number)
                    ELSE TRIM(Tail_Number)
                END AS Tail_Number,

                Origin,
                Dest,
                Reporting_Airline,
                TRY_CAST(AirTime   AS INTEGER) AS AirTime,
                TRY_CAST(Cancelled AS INTEGER) AS Cancelled,
                -- NEW: Dashboard Metric Requirements
                TRY_CAST(Distance AS INTEGER) AS Distance,
                TRY_CAST(DepDelay AS INTEGER) AS DepDelay,
                TRY_CAST(Diverted AS INTEGER) AS Diverted,
                -- -----------------------------------------------------------
                -- CORRECTED MRL LIABILITY FORMULA
                -- Standard formula: (AirTime / 60 × $250) + $180 per cycle
                -- Problem: Legacy logic applied $180 to ALL records, including
                --          cancelled flights — generating phantom liability.
                -- Fix: Hard-zero cancelled flights and null AirTime upstream.
                -- Impact: 96,315 cancelled flights × $180 = $17.3M eliminated.
                -- -----------------------------------------------------------
                CASE
                    WHEN TRY_CAST(Cancelled AS INTEGER) = 1
                      OR TRY_CAST(AirTime   AS INTEGER) IS NULL THEN 0.0
                    ELSE ((TRY_CAST(AirTime AS INTEGER) / 60.0) * 250.0) + 180.0
                END AS MRL_Liability,
                -- -----------------------------------------------------------
                -- ESTIMATED DELAY COST
                -- Logic: $75 per minute of Departure Delay (only positive delays)
                -- -----------------------------------------------------------
                CASE 
                    WHEN TRY_CAST(DepDelay AS INTEGER) > 0 THEN TRY_CAST(DepDelay AS INTEGER) * 75.0 
                    ELSE 0.0 
                END AS Estimated_Cost,

                -- Static counter for Power BI aggregations
                1 AS Flights,
                Reporting_Airline,
                
                -- Ensure these are exposed for the Dimension Tables
                DOT_ID_Reporting_Airline,
                IATA_CODE_Reporting_Airline,
                OriginCityName,
                OriginStateName,
                DestCityName,
                DestStateName,

                -- Delay cause columns: NULL preserved for sparse matrix optimization
                TRY_CAST(ArrDelay          AS INTEGER) AS ArrDelay,
                TRY_CAST(CarrierDelay      AS INTEGER) AS CarrierDelay,
                TRY_CAST(WeatherDelay      AS INTEGER) AS WeatherDelay,
                TRY_CAST(NASDelay          AS INTEGER) AS NASDelay,
                TRY_CAST(SecurityDelay     AS INTEGER) AS SecurityDelay,
                TRY_CAST(LateAircraftDelay AS INTEGER) AS LateAircraftDelay

            FROM read_csv_auto(
                '{DATA_RAW}/*.csv',
                all_varchar=true,
                header=true,
                union_by_name=true
            )
        """)

        # ── Export Fact Table ──────────────────────────────────────────────────
        fact_path = os.path.join(DATA_PROCESSED, 'Aviation_Fact_Table.parquet')
        print("  → Exporting Fact Table (SNAPPY compression)...")
        con.execute(f"""
            COPY bts_flights
            TO '{fact_path}'
            (FORMAT PARQUET, CODEC 'SNAPPY')
        """)
        
        # ── Export Geographic & Airline Dimensions (Star Schema) ───────────────
        print("  → Exporting Airlines and Geo Dimensions...")
        
        # Airlines Dimension
        con.execute(f"COPY (SELECT DISTINCT Reporting_Airline, DOT_ID_Reporting_Airline, IATA_CODE_Reporting_Airline FROM bts_flights WHERE Reporting_Airline IS NOT NULL) TO '{os.path.join(DATA_PROCESSED, 'Aviation_Airlines_Dim.parquet')}' (FORMAT PARQUET, CODEC 'SNAPPY')")
        
        # Geo Dimension (Aliased exactly to match your DAX schema)
        con.execute(f"COPY (SELECT DISTINCT Origin AS AirportCode, OriginCityName AS City, OriginStateName AS State FROM bts_flights UNION SELECT DISTINCT Dest AS AirportCode, DestCityName AS City, DestStateName AS State FROM bts_flights) TO '{os.path.join(DATA_PROCESSED, 'Aviation_Geo_Dim.parquet')}' (FORMAT PARQUET, CODEC 'SNAPPY')")
        # ── Optional: Master Dimension (if FAA Parquet registry exists) ────────
        master_parquet = os.path.join(DATA_RAW, 'FAA_Registry_Master.parquet')
        if os.path.exists(master_parquet):
            print("  → FAA Parquet registry found. Building Master Dimension...")
            con.execute(f"""
                CREATE OR REPLACE VIEW faa_master AS
                SELECT * FROM read_parquet('{master_parquet}')
            """)
            master_dim_path = os.path.join(DATA_PROCESSED, 'Master_Dim.parquet')
            con.execute(f"""
                COPY (
                    SELECT *
                    FROM faa_master
                    WHERE Tail_Number IN (SELECT DISTINCT Tail_Number FROM bts_flights)
                )
                TO '{master_dim_path}'
                (FORMAT PARQUET, CODEC 'SNAPPY')
            """)
            print("  → Master_Dim.parquet exported.")
        else:
            print("  ⚠ FAA_Registry_Master.parquet not found — skipping Master Dim.")
            print("    (Run ghost aircraft audit separately using MASTER.txt)")

        # ── Pipeline Audit Report ──────────────────────────────────────────────
        report = con.execute("""
            SELECT
                COUNT(*)                   AS Total_Rows,
                COUNT(DISTINCT Tail_Number) AS Unique_Aircraft,
                SUM(MRL_Liability)         AS Total_MRL_Liability,
                COUNT(CASE WHEN Cancelled = 1 THEN 1 END) AS Cancelled_Flights
            FROM bts_flights
        """).fetchone()

        print(f"\n  {'─'*44}")
        print(f"  [SILVER] PIPELINE REPORT")
        print(f"  {'─'*44}")
        print(f"  Total Rows Processed  : {report[0]:>12,.0f}")
        print(f"  Unique Aircraft       : {report[1]:>12,.0f}")
        print(f"  Total MRL Liability   : ${report[2]:>12,.2f}")
        print(f"  Cancelled Flights     : {report[3]:>12,.0f}  (hard-zeroed in MRL)")
        print(f"  {'─'*44}\n")

    finally:
        con.close()

# ==============================================================================
# SECTION 4: GHOST AIRCRAFT AUDIT — FAA REGISTRY RECONCILIATION
# ==============================================================================

def run_ghost_aircraft_audit():
    """
    Identifies Ghost Aircraft: tail numbers actively flying in BTS data
    with no corresponding record in the FAA Master Registry.
    Also builds the enriched Master Dimension table by joining ACFTREF.txt.
    """
    print(f"{'='*64}")
    print(f"  [AUDIT] Ghost Aircraft Reconciliation & Dimension Build")
    print(f"{'='*64}")

    master_path  = os.path.join(DATA_RAW, 'MASTER.txt')
    acftref_path = os.path.join(DATA_RAW, 'ACFTREF.txt')
    fact_path    = os.path.join(DATA_PROCESSED, 'Aviation_Fact_Table.parquet')

    # Prerequisite checks
    if not os.path.exists(master_path) or not os.path.exists(acftref_path):
        print("  ⚠ MASTER.txt or ACFTREF.txt not found in data_raw/. Skipping ghost audit.")
        return
    if not os.path.exists(fact_path):
        print("  ⚠ Aviation_Fact_Table.parquet not found. Run Silver pipeline first.\n")
        return

    print("  → Loading FAA Registry (MASTER.txt) and Reference (ACFTREF.txt)...")
    # Read CSVs and strip whitespace from column headers (FAA data is notoriously messy)
    master_df = pd.read_csv(master_path, low_memory=False, dtype=str)
    master_df.columns = master_df.columns.str.strip()
    
    acftref_df = pd.read_csv(acftref_path, low_memory=False, dtype=str)
    acftref_df.columns = acftref_df.columns.str.strip()

    print("  → Merging FAA Relational Tables...")
    # Clean join keys
    master_df['MFR MDL CODE'] = master_df['MFR MDL CODE'].astype(str).str.strip()
    acftref_df['CODE']        = acftref_df['CODE'].astype(str).str.strip()
    
    # Left join to bring MFR and MODEL into the master table
    merged_master = master_df.merge(acftref_df, left_on='MFR MDL CODE', right_on='CODE', how='left')

    print("  → Loading Fact Table tail numbers...")
    fact_tails = pd.read_parquet(fact_path, columns=['Tail_Number'])

    print("  → Standardizing registry keys (N-prefix)...")
    active_fleet                  = set(fact_tails['Tail_Number'].dropna().apply(clean_tail))
    merged_master['N-NUMBER_CLEAN'] = merged_master['N-NUMBER'].apply(clean_tail)
    registered                    = set(merged_master['N-NUMBER_CLEAN'].dropna())

    # ── Core Ghost Aircraft Detection ──────────────────────────────────────────
    orphans = active_fleet - registered

    print(f"\n  {'─'*44}")
    print(f"  [AUDIT] RECONCILIATION RESULTS")
    print(f"  {'─'*44}")
    print(f"  Active Fleet (BTS)    : {len(active_fleet):>8,}  tail numbers")
    print(f"  FAA Registered        : {len(registered):>8,}  tail numbers")
    print(f"  {'─'*41}")
    print(f"  Ghost Aircraft Found  : {len(orphans):>8,}  unregistered tails")
    print(f"  {'─'*44}\n")

    # ── Export Ghost Aircraft List ─────────────────────────────────────────────
    ghost_df   = pd.DataFrame(sorted(orphans), columns=['Ghost_Tail_Number'])
    ghost_path = os.path.join(DATA_PROCESSED, 'Ghost_Aircraft_Audit.parquet')
    ghost_df.to_parquet(ghost_path, index=False)
    print(f"  → Ghost_Aircraft_Audit.parquet exported ({len(orphans)} records).")

    # ── Export Matched Master Dimension ───────────────────────────────────────
    master_matched = merged_master[merged_master['N-NUMBER_CLEAN'].isin(active_fleet)].copy()
    master_matched['N-NUMBER'] = master_matched['N-NUMBER_CLEAN']
    
    # Select target columns now that we successfully merged them
    target_cols = ['N-NUMBER', 'MFR', 'MODEL', 'YEAR MFR', 'TYPE-ACFT', 'NO-SEATS']
    
    # Safely select only columns that actually exist to prevent KeyErrors
    available_cols = [c for c in target_cols if c in master_matched.columns]
    
    master_dim_path = os.path.join(DATA_PROCESSED, 'Master_Dim.parquet')
    master_matched[available_cols].to_parquet(master_dim_path, index=False)
    print(f"  → Master_Dim.parquet exported ({len(master_matched):,} matched records).")
    print(f"  [AUDIT] Complete.\n")


# ==============================================================================
# SECTION 5: EXECUTION GATE
# ==============================================================================

if __name__ == "__main__":

    print("\n" + "="*64)
    print("  US AVIATION RELIABILITY PIPELINE — FY2024")
    print("  Author  : Momin Khan")
    print("  Scale   : 7.07M BTS Flight Records | US Domestic")
    print("  Output  : /data_processed/ — 4x SNAPPY Parquet files")
    print("="*64)

    # STEP 1 — Bronze: Download & Extract BTS data
    # Uncomment if running for the first time:
    download_and_extract()

    # STEP 2 — Silver: DuckDB vectorized ETL & financial modeling
    run_silver_pipeline()

    # STEP 3 — Audit: Ghost aircraft reconciliation
    run_ghost_aircraft_audit()

    print("="*64)
    print("  PIPELINE COMPLETE")
    print("  Artifacts saved to: /data_processed/")
    print("    ├── Aviation_Fact_Table.parquet")
    print("    ├── Master_Dim.parquet")
    print("    └── Ghost_Aircraft_Audit.parquet")
    print("    └── Aviation_Airlines_Dim.parquet")
    print("    └── Aviation_Geo_Dim.parquet")
    print("="*64 + "\n")
