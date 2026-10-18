
import streamlit as st

st.set_page_config(
    page_title="Workplace Safety Sentinel",
    page_icon="🦺",
    layout="wide"
)

# Sidebar
st.sidebar.title("🦺 Safety Sentinel")
st.sidebar.caption("Workplace Monitoring System")
st.sidebar.divider()

st.sidebar.subheader("Monitoring Settings")
location = st.sidebar.selectbox(
    "Workplace Area",
    ["Factory Floor", "Warehouse", "Construction Site", "Office"]
)

st.sidebar.info(
    "Current mode: Image Upload\n\n"
    "AI hazard detection is not connected yet."
)

# Main dashboard
st.title("🦺 Workplace Safety Sentinel")
st.write(
    "A computer-vision prototype for identifying "
    "potential workplace safety risks."
)

st.divider()

# Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Safety Status", "Awaiting Analysis")

with col2:
    st.metric("Hazards Detected", "—")

with col3:
    st.metric("Workplace Area", location)

st.divider()

# Image upload
st.header("📷 Workplace Image Analysis")
st.write(
    "Upload an image of a workplace to begin a safety inspection."
)

uploaded_file = st.file_uploader(
    "Choose a workplace image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    st.image(
        uploaded_file,
        caption="Uploaded Workplace Image",
        use_container_width=True
    )

    st.success("Image uploaded successfully!")

    st.warning(
        "Image received. Automated hazard detection "
        "has not been implemented yet."
    )
else:
    st.info(
        "No image uploaded. Choose a JPG or PNG image to get started."
    )

st.divider()

st.subheader("Planned Safety Checks")

st.write("The prototype will work toward checking for:")
st.markdown(
    """
    - 🪖 Missing protective equipment (PPE)
    - 🔥 Potential fire and smoke hazards
    - 🚧 Unsafe or obstructed work areas
    - ⚠️ Other visible workplace safety risks
    """
)

st.caption(
    "Hack With Bengaluru 4.0 | Prototype in development"
)
