import json
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
VIDEO_PATH = BASE_DIR / "annotated_video.mp4"
INCIDENTS_PATH = BASE_DIR / "incidents.json"
ORIGINAL_VIDEO = BASE_DIR / "people.mp4"

st.set_page_config(
    page_title="Safety Sentinel",
    page_icon="🦺",
    layout="wide"
)

st.title("🦺 Workplace Safety Sentinel")
st.caption("Computer vision | Restricted-zone monitoring")

st.sidebar.title("🦺 Safety Sentinel")
area = st.sidebar.selectbox(
    "Workplace area",
    ["Factory Floor", "Warehouse", "Construction Site", "Office"]
)
st.sidebar.write(f"**Selected area:** {area}")
st.sidebar.info(
    "Current capability: person detection and "
    "potential restricted-zone entry logging."
)

# Load the latest incident records.
incidents = []
if INCIDENTS_PATH.exists():
    try:
        with open(INCIDENTS_PATH, "r") as file:
            incidents = json.load(file)
        if not isinstance(incidents, list):
            incidents = []
    except (json.JSONDecodeError, OSError):
        st.error("Could not read incidents.json.")

if not isinstance(incidents, list):
    incidents = []

# Summary metrics.
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Logged incidents", len(incidents))

with col2:
    unique_people = {
        item.get("track_id")
        for item in incidents
        if item.get("track_id") is not None
    }
    st.metric("Tracked IDs in incident log", len(unique_people))

with col3:
    status = "Review required" if incidents else "No logged entries"
    st.metric("Monitoring status", status)

if incidents:
    st.warning(
        "Potential restricted-zone entries were logged. "
        "A supervisor should review the evidence."
    )
else:
    st.info(
        "No incidents are currently recorded in the log. "
        "This does not guarantee that the workplace is safe."
    )

st.divider()

# Display the processed video.
st.header("🎥 Processed workplace footage")

if VIDEO_PATH.exists():
    st.video(str(VIDEO_PATH))
    st.download_button(
        "Download annotated video",
        data=VIDEO_PATH.read_bytes(),
        file_name="annotated_video.mp4",
        mime="video/mp4"
    )
else:
    st.warning(
        "No processed video found. Run sentinel.py first."
    )

with st.expander("View original footage"):
    if ORIGINAL_VIDEO.exists():
        st.video(str(ORIGINAL_VIDEO))
    else:
        st.info("people.mp4 was not found.")

st.divider()

# Incident table and downloadable evidence log.
st.header("🚨 Incident history")

if incidents:
    df = pd.DataFrame(incidents)
    preferred = [
        "incident_id", "timestamp", "event",
        "track_id", "confidence", "zone", "recorded_at"
    ]
    columns = [c for c in preferred if c in df.columns]
    df = df[columns]

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "Download incident log (JSON)",
        data=json.dumps(incidents, indent=2),
        file_name="incidents.json",
        mime="application/json"
    )

    st.download_button(
        "Download incident report (CSV)",
        data=df.to_csv(index=False),
        file_name="incident_report.csv",
        mime="text/csv"
    )
else:
    st.write("No incident records are available yet.")

st.divider()

st.subheader("How this prototype works")
st.markdown(
    """
    1. YOLOv8 detects people in workplace footage.
    2. Tracking IDs help identify individual people across frames.
    3. A configurable polygon marks the restricted zone.
    4. Potential entries are recorded with timestamps and confidence.
    5. A supervisor can review the video and incident records.
    """
)

st.caption(
    "Hack With Bengaluru 4.0 | Prototype, not a certified "
    "workplace safety system. Results can contain false alarms."
)
