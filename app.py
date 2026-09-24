"""Interactive ISRO mission-launch analytics dashboard.

Run locally with: streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="ISRO Launch Analytics", page_icon="🚀", layout="wide")

DATA_DIR = Path(__file__).parent / "data"
# The dataset was committed to the repo as "ISRO mission launches.csv" (with
# spaces), but the app was written expecting "ISRO_mission_launches.csv"
# (with underscores). That mismatch causes a FileNotFoundError on every
# deployment target (Streamlit Cloud, Render, etc.), since the container's
# filesystem is case- and character-sensitive just like the repo.
#
# Fix: rename the file in the repo to the underscore form (recommended —
# see README) so this simple path works everywhere:
DATA_PATH = DATA_DIR / "ISRO_mission_launches.csv"


def _resolve_data_path() -> Path:
    """Fall back to the space-separated filename if the renamed file isn't
    present yet, so the app still runs even before the repo rename lands."""
    if DATA_PATH.exists():
        return DATA_PATH
    legacy_path = DATA_DIR / "ISRO mission launches.csv"
    if legacy_path.exists():
        return legacy_path
    raise FileNotFoundError(
        f"Could not find the dataset in {DATA_DIR}. Expected "
        f"'{DATA_PATH.name}' (or the legacy '{legacy_path.name}')."
    )


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    """Load and clean the supplied CSV dataset."""
    df = pd.read_csv(path, encoding="latin1")
    df.columns = [
        "serial_no",
        "mission_name",
        "launch_date",
        "launch_vehicle_mission",
        "orbit_type",
        "application",
        "remarks",
    ]

    df["launch_date"] = pd.to_datetime(df["launch_date"], format="%d-%b-%y", errors="coerce")
    df["year"] = df["launch_date"].dt.year
    df["decade"] = (df["year"] // 10 * 10).astype("Int64").astype(str) + "s"
    df["application"] = df["application"].fillna("Not specified")
    df["orbit_type"] = df["orbit_type"].fillna("Not specified")

    df["outcome"] = "Unsuccessful / other"
    df.loc[df["remarks"].eq("Launch successful"), "outcome"] = "Successful"
    df.loc[df["remarks"].str.contains("Partial", case=False, na=False), "outcome"] = "Partial failure"

    conditions = [
        df["launch_vehicle_mission"].str.contains("PSLV", case=False, na=False),
        df["launch_vehicle_mission"].str.contains("GSLV", case=False, na=False),
        df["launch_vehicle_mission"].str.contains("SSLV", case=False, na=False),
        df["launch_vehicle_mission"].str.contains(r"LVM3|Mk III", case=False, na=False, regex=True),
        df["launch_vehicle_mission"].str.contains("Ariane", case=False, na=False),
    ]
    labels = ["PSLV", "GSLV", "SSLV", "LVM3 / GSLV Mk III", "Ariane"]
    df["vehicle_family"] = "Other / international"
    for condition, label in zip(conditions, labels):
        df.loc[condition, "vehicle_family"] = label

    return df.sort_values("launch_date", ascending=False).reset_index(drop=True)


def success_rate(frame: pd.DataFrame) -> float:
    return 100 * frame["outcome"].eq("Successful").mean() if len(frame) else 0.0


df = load_data(_resolve_data_path())

st.title("🚀 ISRO Mission Launch Analytics")
st.caption(
    "An interactive exploratory analysis of the supplied ISRO mission-launch dataset "
    f"({df['launch_date'].min():%d %b %Y} to {df['launch_date'].max():%d %b %Y})."
)

with st.sidebar:
    st.header("Filters")
    min_year, max_year = int(df["year"].min()), int(df["year"].max())
    year_range = st.slider("Launch year", min_year, max_year, (min_year, max_year))
    vehicle_options = sorted(df["vehicle_family"].unique())
    selected_vehicles = st.multiselect("Vehicle family", vehicle_options, default=vehicle_options)
    outcome_options = sorted(df["outcome"].unique())
    selected_outcomes = st.multiselect("Outcome", outcome_options, default=outcome_options)
    application_options = sorted(df["application"].unique())
    selected_applications = st.multiselect("Application", application_options, default=application_options)

filtered = df[
    df["year"].between(*year_range)
    & df["vehicle_family"].isin(selected_vehicles)
    & df["outcome"].isin(selected_outcomes)
    & df["application"].isin(selected_applications)
].copy()

if filtered.empty:
    st.warning("No records match the selected filters. Adjust the filters to continue.")
    st.stop()

st.subheader("Live overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Mission records", f"{len(filtered):,}")
c2.metric("Successful launches", f"{(filtered['outcome'] == 'Successful').sum():,}")
c3.metric("Success rate", f"{success_rate(filtered):.1f}%")
c4.metric("Active years", f"{filtered['year'].nunique():,}")

left, right = st.columns(2)
with left:
    annual = filtered.groupby("year", as_index=False).size().rename(columns={"size": "missions"})
    fig = px.line(
        annual,
        x="year",
        y="missions",
        markers=True,
        title="How did launch activity change over time?",
        labels={"year": "Launch year", "missions": "Mission records"},
    )
    st.plotly_chart(fig, width="stretch")

with right:
    vehicle_counts = (
        filtered["vehicle_family"].value_counts().rename_axis("vehicle_family").reset_index(name="missions")
    )
    fig = px.bar(
        vehicle_counts.sort_values("missions"),
        x="missions",
        y="vehicle_family",
        orientation="h",
        title="Which vehicle families appear most often?",
        labels={"vehicle_family": "Vehicle family", "missions": "Mission records"},
    )
    st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)
with left:
    application_counts = (
        filtered["application"].value_counts().rename_axis("application").reset_index(name="missions")
    )
    fig = px.bar(
        application_counts.head(10).sort_values("missions"),
        x="missions",
        y="application",
        orientation="h",
        title="What mission applications dominate the data?",
        labels={"application": "Application", "missions": "Mission records"},
    )
    st.plotly_chart(fig, width="stretch")

with right:
    outcome_counts = filtered["outcome"].value_counts().rename_axis("outcome").reset_index(name="missions")
    fig = px.pie(
        outcome_counts,
        names="outcome",
        values="missions",
        title="What were the recorded mission outcomes?",
        hole=0.42,
    )
    st.plotly_chart(fig, width="stretch")

st.subheader("Orbit and reliability analysis")
left, right = st.columns(2)
with left:
    orbit_counts = filtered["orbit_type"].value_counts().rename_axis("orbit_type").reset_index(name="missions")
    fig = px.bar(
        orbit_counts.sort_values("missions"),
        x="missions",
        y="orbit_type",
        orientation="h",
        title="Which orbit types are represented?",
        labels={"orbit_type": "Orbit type", "missions": "Mission records"},
    )
    st.plotly_chart(fig, width="stretch")

with right:
    reliability = (
        filtered.assign(success=filtered["outcome"].eq("Successful"))
        .groupby("vehicle_family")["success"]
        .agg(["mean", "size"])
        .reset_index()
    )
    reliability.columns = ["vehicle_family", "success_rate", "missions"]
    reliability["success_rate"] *= 100
    fig = px.bar(
        reliability.sort_values("success_rate", ascending=False),
        x="vehicle_family",
        y="success_rate",
        text="missions",
        title="Recorded success rate by vehicle family",
        labels={"vehicle_family": "Vehicle family", "success_rate": "Success rate (%)", "missions": "Records"},
        range_y=[0, 100],
    )
    fig.update_traces(texttemplate="n=%{text}", textposition="outside")
    st.plotly_chart(fig, width="stretch")

st.subheader("Questions answered by the dashboard")
st.markdown(
    """
    - How many mission records are in a chosen period, and what proportion are marked successful?
    - Which years had the most recorded missions?
    - Which launch-vehicle families are most frequently represented?
    - What applications and orbit types occur most often?
    - How do recorded success rates differ across vehicle families?
    """
)

st.subheader("Filtered mission records")
display_columns = [
    "serial_no",
    "mission_name",
    "launch_date",
    "launch_vehicle_mission",
    "vehicle_family",
    "orbit_type",
    "application",
    "outcome",
    "remarks",
]
st.dataframe(filtered[display_columns], width="stretch", hide_index=True)

st.download_button(
    "Download filtered data as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_isro_launch_records.csv",
    mime="text/csv",
)
