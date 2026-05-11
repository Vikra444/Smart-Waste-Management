import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd
import time
import plotly.express as px
import sqlite3
import random
import os
import sys

# Load Global Config
from config import *

# Paths setup for modular structure
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ai_engine.classifier import classifier
from analytics_engine.predictor import predictor
from alerts_engine.notifier import notifier
from route_engine.optimizer import optimizer
from iot_gateway.sensor_simulator import iot_simulator

# pyrefly: ignore [missing-import]
import folium
# pyrefly: ignore [missing-import]
from streamlit_folium import st_folium

# --- SESSION STATE INITIALIZATION ---
if 'system_initialized' not in st.session_state:
    iot_simulator.initialize_iot_grid()
    st.session_state['system_initialized'] = True
    st.session_state['last_sync'] = time.time()

# --- DATABASE CONNECTION CACHING ---
@st.cache_resource
def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def get_bin_data():
    try:
        conn = get_db_connection()
        return pd.read_sql_query("SELECT * FROM bins", conn)
    except Exception as e:
        st.error(f"Database Read Error: {e}")
        return pd.DataFrame()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title=f"{PROJECT_NAME} | Command Center",
    page_icon="🏙️",
    layout="wide",
)

# --- AUTO-REFRESH (DEMO SMOOTHNESS) ---
if 'refresh_count' not in st.session_state:
    st.session_state.refresh_count = 0

# --- ADVANCED UI STYLING ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    .stApp {{ background-color: #0D1117; font-family: 'Outfit', sans-serif; color: #E0E0E0; }}
    
    .status-bar {{
        display: flex; justify-content: space-around; background: #161B22;
        padding: 10px; border-radius: 12px; border: 1px solid #30363D; margin-bottom: 25px;
    }}
    .status-item {{ font-size: 0.8rem; font-weight: 600; color: #8B949E; }}
    .status-ok {{ color: {THEME_COLOR}; }}
    
    .bin-card {{ background: #161B22; border-radius: 20px; padding: 20px; border: 1px solid #30363D; margin-bottom: 20px; }}
    .bin-card:hover {{ border-color: {THEME_COLOR}; transform: translateY(-5px); transition: all 0.3s ease; }}
</style>
""", unsafe_allow_html=True)

# --- TOP SYSTEM STATUS BAR ---
def render_status_bar():
    st.markdown(f"""
    <div class="status-bar">
        <div class="status-item">AI ENGINE: <span class="status-ok">● ACTIVE</span></div>
        <div class="status-item">IOT GRID: <span class="status-ok">● SYNCED</span></div>
        <div class="status-item">ROUTING: <span class="status-ok">● OPTIMAL</span></div>
        <div class="status-item">DATABASE: <span class="status-ok">● CONNECTED</span></div>
    </div>
    """, unsafe_allow_html=True)

render_status_bar()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"<h1 style='color: {THEME_COLOR};'>{PROJECT_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"`SYSTEM v{VERSION}`")
    st.write("---")
    app_page = st.radio("System Menu", ["🌍 City Map Operations", "📊 Sensor Telemetry", "🧠 Vision Diagnostics", "📢 Community Reports"])
    st.write("---")
    if st.button("🔄 Manual IoT Sync"):
        iot_simulator.update_telemetry()
        st.rerun()
    
    # Auto-refresh toggle for demo
    auto_ref = st.toggle("Enable Auto-Refresh (5s)", value=True)

# --- 1. CITY MAP OPERATIONS ---
if app_page == "🌍 City Map Operations":
    st.title("🏙️ Live City Collection Topology")
    bin_data = get_bin_data()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Live Nodes", len(bin_data), "ONLINE")
    with c2: 
        crit_bins = bin_data[bin_data['fill_level'] >= 80]
        st.metric("Priority Targets", len(crit_bins), f"{len(crit_bins)} Required", delta_color="inverse")
    with c3: st.metric("Resource Optimization", "94%", "↑ 12%")
    with c4: st.metric("System Uptime", "99.9%", "Stable")

    st.write("---")
    col_map, col_info = st.columns([2.5, 1])

    with col_map:
        m = folium.Map(location=CITY_CENTER, zoom_start=MAP_ZOOM, tiles="CartoDB dark_matter")
        folium.Marker(DEPOT_LOCATION, popup="Central Depot", icon=folium.Icon(color='blue', icon='home')).add_to(m)
        
        target_list = crit_bins.to_dict('records')
        try:
            route = optimizer.calculate_optimal_path(DEPOT_LOCATION, target_list)
            if route:
                points = [DEPOT_LOCATION] + [[b['lat'], b['lon']] for b in route]
                folium.PolyLine(points, color=THEME_COLOR, weight=5, opacity=0.8, dash_array='10').add_to(m)
        except Exception as e:
            st.error(f"Routing Engine Error: {e}")
            route = []

        for _, b in bin_data.iterrows():
            color = CRITICAL_COLOR if b['fill_level'] >= 80 else WARNING_COLOR if b['fill_level'] >= 60 else THEME_COLOR
            folium.CircleMarker(
                location=[b['lat'], b['lon']],
                radius=10 if b['fill_level'] < 80 else 15,
                popup=f"{b['location']}: {b['fill_level']}%",
                color=color, fill=True, fill_color=color, fill_opacity=0.6,
            ).add_to(m)
            
        st_folium(m, width=900, height=550)

    with col_info:
        st.markdown("<div class='ai-panel' style='background:#161B22; padding:20px; border-radius:20px; border:1px solid #30363D;'>", unsafe_allow_html=True)
        st.subheader("🧠 AI Dispatch Intel")
        if not route:
            st.success("All city sectors are currently optimal.")
        else:
            metrics = optimizer.get_eta_metrics(route)
            st.markdown(f"""
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px;'>
                    <div style='background:#010409; padding:10px; border-radius:10px; border:1px solid {THEME_COLOR}55; text-align:center;'>
                        <small>DISTANCE</small><br><b>{metrics['distance']}</b>
                    </div>
                    <div style='background:#010409; padding:10px; border-radius:10px; border:1px solid {THEME_COLOR}55; text-align:center;'>
                        <small>ETA</small><br><b>{metrics['time']}</b>
                    </div>
                    <div style='background:#010409; padding:10px; border-radius:10px; border:1px solid {THEME_COLOR}55; text-align:center;'>
                        <small>CO2 SAVED</small><br><b style='color:{THEME_COLOR};'>{metrics['co2_reduction']}</b>
                    </div>
                    <div style='background:#010409; padding:10px; border-radius:10px; border:1px solid {THEME_COLOR}55; text-align:center;'>
                        <small>FUEL SAVED</small><br><b style='color:{THEME_COLOR};'>{metrics['fuel_savings']}</b>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("**Recommended Collection Sequence:**")
            for i, b in enumerate(route, 1):
                st.markdown(f"<div style='border-left:4px solid {CRITICAL_COLOR if b['fill_level']>=80 else WARNING_COLOR}; padding-left:10px; margin-bottom:10px;'>{i}. 📍 {b['location']} ({b['fill_level']}%)</div>", unsafe_allow_html=True)
            
            if st.button("🚀 Dispatch & Empty Bins"):
                # Simulate real collection
                target_ids = [b['id'] for b in route]
                iot_simulator.simulate_collection_reset(target_ids)
                st.toast(f"Unit Dispatched! {len(target_ids)} bins emptied.")
                time.sleep(1)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 2. SENSOR TELEMETRY ---
elif app_page == "📊 Sensor Telemetry":
    st.title("📊 Detailed Node Telemetry")
    bin_data = get_bin_data()
    
    if bin_data.empty:
        st.warning("No data available in the IoT Grid.")
    else:
        rows = [bin_data.iloc[i:i+4] for i in range(0, len(bin_data), 4)]
        for row_df in rows:
            cols = st.columns(4)
            for i, (_, b) in enumerate(row_df.iterrows()):
                with cols[i]:
                    color = CRITICAL_COLOR if b['status'] == 'CRITICAL' else THEME_COLOR
                    st.markdown(f"""
                        <div style='background:#161B22; padding:20px; border-radius:20px; border:1px solid {color}55;'>
                            <h4 style='margin:0;'>{b['location']}</h4>
                            <p style='color:{color}; font-size:1.8rem; margin:10px 0; font-weight:800;'>{b['fill_level']}%</p>
                            <div style='font-size:0.8rem; color:#8B949E;'>
                                🔋 Battery: {b['battery']}%<br>
                                🌡️ Temp: {b['temp']:.1f}°C<br>
                                💨 Gas: {b['gas_level']} ppm
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# --- 3. VISION DIAGNOSTICS ---
elif app_page == "🧠 Vision Diagnostics":
    st.title("🧠 AI Vision Core Diagnostics")
    st.markdown("Automated waste classification and segregation intelligence.")
    
    up = st.file_uploader("Upload waste sample for AI analysis", type=['jpg', 'jpeg', 'png'])
    if up:
        img = Image.open(up).convert("RGB")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(img, caption="Source Image", use_container_width=True)
        with col2:
            with st.spinner("🤖 AI Engine Inferencing..."):
                try:
                    label, conf, guide, timing = classifier.predict(img)
                    st.markdown(f"""
                        <div style='background:#161B22; padding:20px; border-radius:20px; border:1px solid {THEME_COLOR};'>
                            <small style='color:#8B949E;'>AI ANALYSIS RESULT</small>
                            <h2 style='margin:0;'>{label}</h2>
                            <h1 style='color:{THEME_COLOR}; margin:10px 0;'>{conf*100:.1f}%</h1>
                            <p style='margin:0;'><b>Guidance:</b> {guide}</p>
                            <hr style='border: 0.1px solid #30363D; margin: 15px 0;'>
                            <small style='color:#8B949E;'>Inference Speed: {timing}ms</small>
                        </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Inference Error: {e}")

# --- 4. COMMUNITY REPORTS ---
elif app_page == "📢 Community Reports":
    st.title("📢 Citizen Complaint Hub")
    st.markdown("Crowdsourced waste monitoring for community action.")
    
    with st.form("Citizen Report Form"):
        n = st.text_input("Full Name")
        l = st.text_input("Location / Landmark")
        t_issue = st.selectbox("Issue Type", ["Bin Overflow", "Illegal Dumping", "Foul Smell", "Damaged Bin"])
        if st.form_submit_button("Submit Intelligence Report"):
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("INSERT INTO complaints (user_name, location, type, status, timestamp) VALUES (?, ?, ?, ?, ?)", 
                          (n, l, t_issue, "Pending", time.strftime('%Y-%m-%d %H:%M')))
                conn.commit()
                st.success("Report successfully logged in the Global Grid. AI will prioritize dispatch.")
            except Exception as e:
                st.error(f"Report Logging Error: {e}")
    
    st.write("---")
    st.subheader("📋 Recent Community Reports")
    try:
        conn = get_db_connection()
        comp_df = pd.read_sql_query("SELECT user_name as Citizen, location as Location, type as Issue, status as Status FROM complaints ORDER BY id DESC LIMIT 5", conn)
        st.table(comp_df)
    except:
        st.info("No active community reports found.")

# --- AUTO-REFRESH LOGIC ---
if auto_ref:
    time.sleep(REFRESH_INTERVAL)
    iot_simulator.update_telemetry()
    st.rerun()
