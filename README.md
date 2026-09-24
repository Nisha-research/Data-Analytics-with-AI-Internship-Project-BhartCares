# ISRO Mission Launch Analytics

An interactive Streamlit data-analytics project built from the supplied **ISRO mission launches** CSV. The dashboard explores launch activity, mission purpose, orbit type, vehicle-family representation, and recorded outcomes from **19 April 1975 to 2 September 2023**.

## Problem statement

How has the mission-launch portfolio represented in this dataset evolved over time, and what patterns are visible in launch outcomes, vehicle families, mission applications, and destination orbits?

The project turns a static CSV into a filterable dashboard that supports exploratory analysis instead of relying only on fixed summary tables.

## Dataset

- **Source:** User-supplied `ISRO mission launches.csv` file included in this repository as `data/ISRO_mission_launches.csv`.
- **Grain:** One row per mission/satellite record in the source file; a single launch can appear in multiple rows when it carried multiple payloads.
- **Size:** 125 records and 7 original columns.
- **Coverage:** 19 April 1975 through 2 September 2023.
- **Original variables:** Serial number, mission/satellite name, launch date, launch vehicle/mission text, orbit type, application, and remarks.

> **Important interpretation note:** Because multiple payload records can share one launch date and vehicle-mission description, the dashboard reports *mission records*, not necessarily unique physical launch events.

## Key questions answered live

Use the sidebar filters to answer these questions for any selected subset of the data:

1. How many mission records and successful records occurred during the selected years?
2. Which years had the highest recorded mission activity?
3. Which vehicle families occur most often?
4. Which applications and orbit types dominate the records?
5. How do recorded success rates compare by vehicle family?
6. Which individual mission records match the current filters?

## Analysis steps

1. **Ingest** the supplied CSV using `latin1` encoding because its text includes non-UTF-8 characters.
2. **Rename** columns to analysis-friendly snake_case labels.
3. **Parse** launch dates and derive `year` and `decade` fields.
4. **Treat missing values** in `application` and `orbit_type` as `Not specified` so record counts remain transparent.
5. **Classify outcomes** from `remarks` as `Successful`, `Partial failure`, or `Unsuccessful / other`.
6. **Derive vehicle families** from the vehicle/mission text: PSLV, GSLV, SSLV, LVM3 / GSLV Mk III, Ariane, or Other / international.
7. **Visualize and filter** the results in Streamlit with Plotly charts and a downloadable table.

## Verified baseline findings

These findings refer to the full supplied dataset before dashboard filters are applied:

- **125** mission records span **1975–2023**.
- **112 records (89.6%)** have remarks of `Launch successful`.
- **PSLV** is the most represented vehicle family, with **61** records.
- The dataset contains the most records in **2018** and **2022** (**9 each**).
- **Communication (38)** and **Earth Observation (36)** are the two most common application labels.
- **GSO (42)** and **SSPO (37)** are the most common stated orbit types; **21** records do not specify an orbit type.

## Project structure

```text
isro-launch-analytics/
├── app.py                         # Streamlit application
├── requirements.txt               # Python dependencies
├── README.md                      # GitHub project documentation
├── project_report.md              # Detailed analysis report
└── data/
    └── ISRO_mission_launches.csv  # Supplied dataset
```

## Run locally

```bash
git clone <your-repository-url>
cd isro-launch-analytics
python -m venv .venv
```

Activate the virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install dependencies and start the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit will print a local URL, typically `http://localhost:8501`.

## Suggested GitHub workflow

```bash
git init
git add .
git commit -m "Build ISRO mission launch analytics dashboard"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```

## Limitations

- The analysis is limited to the supplied file, which ends on **2 September 2023**; it is not a complete or current ISRO launch registry.
- The dataset mixes satellite/payload records with launch information, so rows should not automatically be interpreted as unique launches.
- Vehicle families are inferred from free-text launch vehicle descriptions; unusual descriptions fall into `Other / international`.
- A remark such as `Failed in Orbit` is not counted as a successful launch outcome in the dashboard’s derived outcome field.

