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

# A polygon representing coordinates of a designated safe grazing pasture zone
fence_coordinates = [
    (11.9800, 8.5200),
    (11.9950, 8.5200),
    (11.9950, 8.5400),
    (11.9800, 8.5400)
]
safe_zone_polygon = Polygon(fence_coordinates)

# ==========================================
# 3. SIDEBAR CONTROLS FOR DEFENSE PRESENTATION
# ==========================================

st.sidebar.header("🕹️ Simulation Control Unit")
sim_speed = st.sidebar.slider("IoT Transmission Interval (Seconds)", 0.5, 3.0, 1.0)
num_packets = st.sidebar.number_input("Total Data Packets to Stream", min_value=10, max_value=200, value=30)

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================

# Mocked SVR Prediction Function mirroring your empirical findings (R²: 0.9992, MAE: 0.1343)
def execute_svr_forecast(temp, humidity, activity):
    # Mimics the deterministic target relationship calculated by your trained SVR model
    raw_score = (temp * 0.018) + (activity * 0.06) - (humidity * 0.004)
    normalized_intensity = 1 / (1 + np.exp(-raw_score + 1))  # Scales between 0 and 1
    return round(float(normalized_intensity), 4)

# ==========================================
# 5. INITIALIZE PLACEHOLDERS FOR DYNAMIC UI
# ==========================================

kpi_row = st.empty()
map_container = st.empty()
chart_container = st.empty()

if 'telemetry_log' not in st.session_state:
    st.session_state.telemetry_log = []

# ==========================================
# 6. LIVE SIMULATION EXECUTION LOOP
# ==========================================

if st.sidebar.button("🚀 Run Live IoT Simulation"):
    st.sidebar.info("Streaming continuous chunks of data from collars...")
    
    # Generate mock positional trajectories stepping across boundaries
    latitudes = np.linspace(11.9830, 11.9980, num_packets) + np.random.normal(0, 0.001, num_packets)
    longitudes = np.linspace(8.5250, 8.5430, num_packets) + np.random.normal(0, 0.001, num_packets)
    ambient_temps = np.random.uniform(30.0, 42.0, num_packets)  # Typical Sahel range
    humidities = np.random.uniform(15.0, 55.0, num_packets)
    activity_metrics = np.random.uniform(2.0, 9.5, num_packets)
    
    for idx in range(num_packets):
        current_lat = latitudes[idx]
        current_lon = longitudes[idx]
        current_temp = ambient_temps[idx]
        current_hum = humidities[idx]
        current_act = activity_metrics[idx]

        # Geofencing Point-in-Polygon Check
        livestock_point = Point(current_lat, current_lon)
        inside_fence = safe_zone_polygon.contains(livestock_point)
        boundary_status = "SAFE" if inside_fence else "TRESPASSING"

        # Run the predictive analytical score
        predicted_intensity = execute_svr_forecast(current_temp, current_hum, current_act)
        overgrazing_risk = "CRITICAL HIGH" if predicted_intensity > 0.72 else "NORMAL"

        # Append to historical buffer
        packet_record = {
            "Time": time.strftime("%H:%M:%S"),
            "Lat": current_lat,
            "Lon": current_lon,
            "Temp (°C)": current_temp,
            "Humidity (%)": current_hum,
            "Activity": current_act,
            "SVR Grazing Intensity": predicted_intensity,
            "Status": boundary_status,
            "Risk Assessment": overgrazing_risk
        }
        st.session_state.telemetry_log.append(packet_record)
        df_current = pd.DataFrame(st.session_state.telemetry_log)

        # Render real-time Key Performance Indicators (KPIs)
        with kpi_row.container():
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

        # Send ephemeral toast alert on boundary breach
        if boundary_status == "TRESPASSING":
            st.toast(f"⚠️ Breach Detected! Livestock crossed virtual boundary line at ({current_lat:.4f}, {current_lon:.4f})", icon="🚨")

        # Render geospatial mapping using Folium
        with map_container.container():
            st.markdown("### 🗺️ System Visualization: Virtual Fence & Animal Trajectory")
            m = folium.Map(location=[11.9875, 8.5300], zoom_start=14)
            
            # Draw defined fence polygon
            folium.Polygon(
                locations=fence_coordinates,
                color="#FF0000",
                weight=3,
                fill=True,
                fill_color="#00FF00" if inside_fence else "#FFCC00",
                fill_opacity=0.15,
                popup="Predefined Virtual Grazing Boundary"
            ).add_to(m)

            # Drop marker at current livestock location
            marker_color = "green" if (inside_fence and overgrazing_risk == "NORMAL") else "red"
            folium.Marker(
                location=[current_lat, current_lon],
                popup=f"Status: {boundary_status} | Grazing Metric: {predicted_intensity}",
                icon=folium.Icon(color=marker_color, icon="bolt" if not inside_fence else "ok-sign")
            ).add_to(m)
            
            st_folium(m, width=1000, height=400, key=f"folium_map_tick_{idx}")

        # Render real-time analytics graphs
        with chart_container.container():
            st.markdown("### 📈 Time-Series Evaluation (IoT Environment Data vs Predictive Yield)")
            st.line_chart(df_current.set_index("Time")[["SVR Grazing Intensity", "Temp (°C)"]])
            
        time.sleep(sim_speed)
        
    st.success("✅ Simulation stream sequence finalized successfully!")
    st.markdown("### 📋 Captured Telemetry Ledger (Processed IoT Packets)")
    st.dataframe(df_current)
