# ISRO Mission Launch Analytics — Project Report

## 1. Executive summary

This project analyzes the supplied ISRO mission-launch dataset and delivers a Streamlit dashboard for live exploration. The source contains **125 mission records** from **19 April 1975** through **2 September 2023**. The dashboard allows a user to filter records by year, launch-vehicle family, outcome, and application, then inspect mission volume, outcome mix, application focus, orbit categories, vehicle prevalence, and reliability indicators.

The analysis finds that records increase markedly in the 2010s, with the largest annual totals in **2018** and **2022** (nine records each). **PSLV** is the most frequently represented vehicle family (61 records), and **Communication** and **Earth Observation** are the leading mission applications. The source remarks mark 112 of 125 records (**89.6%**) as `Launch successful`.

## 2. Problem statement

The goal is to understand the historical mission profile represented in the dataset and enable stakeholders to answer:

- How did recorded mission activity vary over time?
- Which launch-vehicle families were used most often?
- What mission applications and orbit types were most prevalent?
- What outcomes are recorded, and how do they vary across vehicle families?

## 3. Dataset description

### Source and scope

The data is the user-provided CSV file, stored in the project at `data/ISRO_mission_launches.csv`. It has 125 rows and seven original fields.

| Field | Description |
|---|---|
| `SL No` | Source serial number |
| `Launch Date` | Mission/satellite label in the supplied file despite its header |
| `Launch Vehicle` | Launch date in `DD-Mon-YY` format despite its header |
| `Launch Vehicle.1` | Free-text launch vehicle / mission descriptor |
| `Orbit Type` | Target orbit category, when available |
| `Application` | Mission purpose/category, when available |
| `Remarks` | Recorded status or outcome description |

### Data-quality observations

The CSV headers are shifted relative to their apparent values. The project explicitly renames them after inspection so that the values are represented correctly. It also uses `latin1` encoding because the file includes characters that cannot be decoded as UTF-8.

Missing values occur in:

- `Orbit Type`: 21 records
- `Application`: 4 records

These are labeled `Not specified` in the dashboard instead of being removed.

## 4. Methodology

### Cleaning and transformation

1. Loaded the CSV using `latin1` encoding.
2. Reassigned descriptive column names matching the observed values.
3. Converted launch dates with the `%d-%b-%y` date format.
4. Created `year` and `decade` temporal fields.
5. Standardized missing applications and orbit types as `Not specified`.
6. Created a derived `outcome` category based on `remarks`:
   - `Launch successful` → `Successful`
   - Text containing `Partial` → `Partial failure`
   - All remaining labels → `Unsuccessful / other`
7. Inferred `vehicle_family` from the free-text mission description: PSLV, GSLV, SSLV, LVM3 / GSLV Mk III, Ariane, or Other / international.

### Analytical approach

The dashboard uses descriptive analytics rather than predictive modeling. It provides counts, proportions, time trends, group comparisons, and record-level drill-down. The charts dynamically recalculate after the user applies sidebar filters.

## 5. Baseline results

### Overall outcome profile

| Metric | Result |
|---|---:|
| Mission records | 125 |
| Date range | 19 Apr 1975 – 02 Sep 2023 |
| Records marked `Launch successful` | 112 |
| Recorded success rate | 89.6% |
| Records marked non-successful / other | 11 |
| Records marked partial failure | 1 |

### Vehicle-family representation

| Vehicle family | Records |
|---|---:|
| PSLV | 61 |
| Ariane | 25 |
| GSLV | 18 |
| Other / international | 18 |
| SSLV | 2 |
| LVM3 / GSLV Mk III | 1 |

### Mission focus

The two leading applications are:

- Communication: 38 records
- Earth Observation: 36 records

The two leading stated orbit categories are:

- GSO (Geosynchronous Orbit): 42 records
- SSPO (Sun Synchronous Polar Orbit): 37 records

## 6. Key findings

1. **Mission activity is concentrated in recent decades.** The 2010s account for 56 of 125 records, more than any earlier decade in the supplied data.
2. **PSLV dominates the dataset.** With 61 records, PSLV accounts for nearly half of all listed records and is central to the historical mission mix captured here.
3. **The portfolio emphasizes communications and Earth observation.** Together, these application labels appear in 74 records before counting mixed-category labels.
4. **Orbit data points primarily to GSO and sun-synchronous missions.** These stated categories lead the orbit distribution, consistent with communications and Earth-observation use cases in the dataset.
5. **Recorded outcomes are largely successful.** The 89.6% figure reflects the source remarks, not an independently validated engineering reliability rate.
6. **Interpret counts carefully.** Multiple rows can belong to the same launch mission, so the results describe mission/payload records rather than a deduplicated launch-event series.

## 7. Live dashboard capabilities

The Streamlit application supports these live questions:

- What does the selected subset’s success rate look like?
- How many mission records occur each year?
- Which vehicle families occur most frequently in a selected time period?
- Which applications and orbits are dominant after filtering?
- How do outcome rates compare across vehicle families?
- Which underlying records support the chart results?

Users can download the filtered data table as a CSV directly from the dashboard.

## 8. Limitations and next steps

### Limitations

- The dataset is static and ends on 2 September 2023.
- Rows are not guaranteed to represent unique launch events.
- Launch outcome terminology is simplified into a derived analytic category.
- Free-text vehicle classification can misclassify unusual descriptions.

### Recommended next steps

1. Add a unique launch-event identifier and payload count to distinguish launches from individual payload records.
2. Validate the dataset against an authoritative, updated launch registry.
3. Enrich the data with launch site, mission mass, cost, customer type, and payload count.
4. Add automated data-quality tests and a data dictionary.
5. Deploy the Streamlit app through Streamlit Community Cloud or another hosting platform after pushing the repository to GitHub.

