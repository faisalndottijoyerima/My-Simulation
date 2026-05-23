import streamlit as st
import pandas as pd
import numpy as np
import time
from shapely.geometry import Point, Polygon
import folium
from streamlit_folium import st_folium

# ==========================================
# 1. PAGE SETUP & DESIGN
# ==========================================
st.set_page_config(page_title="Intelligent Livestock Framework Dashboard", layout="wide")
st.title("🛰️ Intelligent Livestock Management Dashboard")
st.subheader("Real-Time IoT Telemetry, Geo-Fencing, and Predictive Analytics Core (Chapter 4 Validation)")

# ==========================================
# 2. DEFINING THE VIRTUAL BOUNDARY (GEO-FENCE)
# ==========================================

fence_coordinates = [
    (11.9800, 8.5200),
    (11.9950, 8.5200),
    (11.9950, 8.5400),
    (11.9800, 8.5400),
]
safe_zone_polygon = Polygon(fence_coordinates)

# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================

st.sidebar.header("🕹️ Simulation Control Unit")
sim_speed = st.sidebar.slider("IoT Transmission Interval (Seconds)", 0.5, 3.0, 1.0)
num_packets = st.sidebar.number_input("Total Data Packets to Stream", min_value=10, max_value=200, value=30)

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================


def execute_svr_forecast(temp, humidity, activity):
    raw_score = (temp * 0.018) + (activity * 0.06) - (humidity * 0.004)
    normalized_intensity = 1 / (1 + np.exp(-raw_score + 1))
    return round(float(normalized_intensity), 4)


def process_packet(lat, lon, temp, hum, act, safe_polygon):
    livestock_point = Point(lat, lon)
    inside_fence = safe_polygon.contains(livestock_point)
    boundary_status = "SAFE" if inside_fence else "TRESPASSING"
    predicted_intensity = execute_svr_forecast(temp, hum, act)
    overgrazing_risk = "CRITICAL HIGH" if predicted_intensity > 0.72 else "NORMAL"
    return {
        "Time": time.strftime("%H:%M:%S"),
        "Lat": lat,
        "Lon": lon,
        "Temp (°C)": temp,
        "Humidity (%)": hum,
        "Activity": act,
        "SVR Grazing Intensity": predicted_intensity,
        "Status": boundary_status,
        "Risk Assessment": overgrazing_risk,
        "_inside_fence": inside_fence,
        "_predicted_intensity": predicted_intensity,
        "_boundary_status": boundary_status,
        "_overgrazing_risk": overgrazing_risk,
    }


def render_dashboard(packet, df_current, kpi_slot, map_slot, chart_slot):
    """Draw KPIs, map, and chart into fixed placeholders (survives Streamlit reruns)."""
    current_lat = packet["Lat"]
    current_lon = packet["Lon"]
    predicted_intensity = packet["_predicted_intensity"]
    boundary_status = packet["_boundary_status"]
    overgrazing_risk = packet["_overgrazing_risk"]
    inside_fence = packet["_inside_fence"]

    with kpi_slot.container():
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📍 Active Coordinates", f"{current_lat:.4f}, {current_lon:.4f}")
        c2.metric("📊 SVR Forecasted Intensity", f"{predicted_intensity}")

        if boundary_status == "SAFE":
            c3.success(f"Geofence: {boundary_status}")
        else:
            c3.error(f"Geofence: {boundary_status} 🚨")

        if overgrazing_risk == "NORMAL":
            c4.info(f"Rangeland Risk: {overgrazing_risk}")
        else:
            c4.warning(f"Rangeland Risk: {overgrazing_risk} ⚠️")

    with map_slot.container():
        st.markdown("### 🗺️ System Visualization: Virtual Fence & Animal Trajectory")
        m = folium.Map(location=[11.9875, 8.5300], zoom_start=14)

        folium.Polygon(
            locations=fence_coordinates,
            color="#FF0000",
            weight=3,
            fill=True,
            fill_color="#00FF00" if inside_fence else "#FFCC00",
            fill_opacity=0.15,
            popup="Predefined Virtual Grazing Boundary",
        ).add_to(m)

        marker_color = "green" if (inside_fence and overgrazing_risk == "NORMAL") else "red"
        folium.Marker(
            location=[current_lat, current_lon],
            popup=f"Status: {boundary_status} | Grazing Metric: {predicted_intensity}",
            icon=folium.Icon(color=marker_color, icon="bolt" if not inside_fence else "ok-sign"),
        ).add_to(m)

        # Stable key — changing keys remount the map and trigger extra reruns (blank flicker).
        st_folium(m, width=1000, height=400, key="livestock_map")

    with chart_slot.container():
        st.markdown("### 📈 Time-Series Evaluation (IoT Environment Data vs Predictive Yield)")
        display_df = df_current.drop(
            columns=[c for c in df_current.columns if c.startswith("_")],
            errors="ignore",
        )
        st.line_chart(display_df.set_index("Time")[["SVR Grazing Intensity", "Temp (°C)"]])


def telemetry_to_dataframe(log):
    df = pd.DataFrame(log)
    return df.drop(columns=[c for c in df.columns if c.startswith("_")], errors="ignore")


# ==========================================
# 5. SESSION STATE
# ==========================================

if "telemetry_log" not in st.session_state:
    st.session_state.telemetry_log = []
if "sim_running" not in st.session_state:
    st.session_state.sim_running = False
if "sim_idx" not in st.session_state:
    st.session_state.sim_idx = 0
if "simulation_complete" not in st.session_state:
    st.session_state.simulation_complete = False

kpi_row = st.empty()
map_container = st.empty()
chart_container = st.empty()
status_area = st.empty()

# ==========================================
# 6. START / STEP SIMULATION (rerun-safe)
# ==========================================

if st.sidebar.button("🚀 Run Live IoT Simulation"):
    st.session_state.telemetry_log = []
    st.session_state.sim_idx = 0
    st.session_state.sim_running = True
    st.session_state.simulation_complete = False

    n = int(num_packets)
    st.session_state.sim_latitudes = (
        np.linspace(11.9830, 11.9980, n) + np.random.normal(0, 0.001, n)
    )
    st.session_state.sim_longitudes = (
        np.linspace(8.5250, 8.5430, n) + np.random.normal(0, 0.001, n)
    )
    st.session_state.sim_temps = np.random.uniform(30.0, 42.0, n)
    st.session_state.sim_humidities = np.random.uniform(15.0, 55.0, n)
    st.session_state.sim_activities = np.random.uniform(2.0, 9.5, n)
    st.session_state.sim_total = n

if st.session_state.sim_running:
    idx = st.session_state.sim_idx
    total = st.session_state.sim_total

    if idx < total:
        st.sidebar.info(f"Streaming packet {idx + 1} of {total}…")

        packet = process_packet(
            st.session_state.sim_latitudes[idx],
            st.session_state.sim_longitudes[idx],
            st.session_state.sim_temps[idx],
            st.session_state.sim_humidities[idx],
            st.session_state.sim_activities[idx],
            safe_zone_polygon,
        )
        st.session_state.telemetry_log.append(packet)
        st.session_state.sim_idx = idx + 1

        df_current = pd.DataFrame(st.session_state.telemetry_log)
        render_dashboard(packet, df_current, kpi_row, map_container, chart_container)

        if packet["_boundary_status"] == "TRESPASSING":
            st.toast(
                f"⚠️ Breach Detected! Livestock crossed virtual boundary at "
                f"({packet['Lat']:.4f}, {packet['Lon']:.4f})",
                icon="🚨",
            )

        if st.session_state.sim_idx < total:
            time.sleep(sim_speed)
            st.rerun()
        else:
            st.session_state.sim_running = False
            st.session_state.simulation_complete = True

elif st.session_state.telemetry_log:
    # Rerun after map/widget interaction — redraw last frame so the UI does not go blank.
    last_packet = st.session_state.telemetry_log[-1]
    df_current = pd.DataFrame(st.session_state.telemetry_log)
    render_dashboard(last_packet, df_current, kpi_row, map_container, chart_container)

if st.session_state.simulation_complete and st.session_state.telemetry_log:
    df_display = telemetry_to_dataframe(st.session_state.telemetry_log)
    with status_area.container():
        st.success("✅ Simulation stream sequence finalized successfully!")
        st.markdown("### 📋 Captured Telemetry Ledger (Processed IoT Packets)")
        st.dataframe(df_display)
