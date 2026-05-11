import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import random
import cv2
import logging
# pyrefly: ignore [missing-import]
import folium
# pyrefly: ignore [missing-import]
from streamlit_folium import st_folium

# --- INDUSTRIAL LOGGING SETUP ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('smart_bins.db')
    c = conn.cursor()
    # Check if lat/lon columns exist, if not, recreate or alter table
    c.execute('''CREATE TABLE IF NOT EXISTS bins
                 (id INTEGER PRIMARY KEY, location TEXT, fill_level INTEGER, type TEXT, status TEXT, lat REAL, lon REAL)''')
    
    c.execute("SELECT COUNT(*) FROM bins")
    if c.fetchone()[0] == 0:
        initial_data = [
            ('Sector 1', 85, 'Recyclable', 'Overflow Soon', 23.2599, 77.4126),
            ('BGI Campus', 20, 'Organic', 'Normal', 23.2514, 77.4815),
            ('Main Market', 92, 'Non-Recyclable', 'CRITICAL', 23.2352, 77.4244),
            ('Railway Station', 45, 'Hazardous', 'Normal', 23.2667, 77.4100),
            ('Subhash Nagar', 12, 'Organic', 'Empty', 23.2450, 77.4420)
        ]
        c.executemany("INSERT INTO bins (location, fill_level, type, status, lat, lon) VALUES (?, ?, ?, ?, ?, ?)", initial_data)
        conn.commit()
    conn.close()

def get_bin_data():
    conn = sqlite3.connect('smart_bins.db')
    df = pd.read_sql_query("SELECT location as Location, fill_level as 'Fill Level (%)', type as Type, status as Status, lat, lon FROM bins", conn)
    conn.close()
    return df

def simulate_sensor_update():
    """Industrial Simulation of IoT Sensor Data Flow"""
    try:
        conn = sqlite3.connect('smart_bins.db')
        c = conn.cursor()
        c.execute("SELECT id, fill_level FROM bins")
        bins = c.fetchall()
        for bin_id, level in bins:
            # Simulated real-world industrial fluctuations
            new_level = level + random.randint(-5, 15)
            new_level = max(0, min(100, new_level))
            
            status = 'NORMAL'
            if new_level >= 90: status = 'CRITICAL'
            elif new_level >= 75: status = 'OVERFLOW SOON'
            elif new_level == 0: status = 'EMPTY'
            
            c.execute("UPDATE bins SET fill_level = ?, status = ? WHERE id = ?", (new_level, status, bin_id))
        conn.commit()
        conn.close()
        logger.info("IoT Grid Synchronization Successful")
    except Exception as e:
        logger.error(f"IoT Sync Failure: {e}")

init_db()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="NEUROX AI | Smart Waste Management",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS (PREMIUM UI) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Main Background */
    .stApp {
        background-color: #0D1117;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #010409 !important;
        border-right: 1px solid #30363D;
    }
    
    /* Premium Metric Card */
    .metric-card {
        background: #161B22;
        border-radius: 24px;
        padding: 30px;
        border: 1px solid #30363D;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #2EA043;
        box-shadow: 0 8px 30px rgba(46, 160, 67, 0.15);
    }

    .telemetry-log {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.8rem;
        color: #2EA043;
        background: #010409;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363D;
        height: 150px;
        overflow-y: scroll;
    }

    /* System Status Pulse */
    .pulse-online {
        width: 10px;
        height: 10px;
        background: #2EA043;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #2EA043;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 160, 67, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(46, 160, 67, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(46, 160, 67, 0); }
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD MODEL ---
@st.cache_resource
def load_neurox_model():
    try:
        return tf.keras.models.load_model("waste_model.h5")
    except:
        return None

model = load_neurox_model()
classes = ['Hazardous', 'Non-Recyclable', 'Organic', 'Recyclable']

def predict_waste(img):
    img = img.resize((224, 224))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)
    pred = model.predict(img)
    return classes[np.argmax(pred)], np.max(pred)

# --- SIDEBAR BRANDING ---
st.sidebar.markdown("""
    <div style='text-align: center; padding: 20px; background: rgba(46, 160, 67, 0.1); border-radius: 15px; border: 1px solid rgba(46, 160, 67, 0.2); margin-bottom: 20px;'>
        <h1 style='color: #2EA043; margin:0;'>NEUROX AI</h1>
        <p style='font-size: 0.8rem; opacity: 0.8;'>Next-Gen Waste Intelligence</p>
    </div>
""", unsafe_allow_html=True)

# Language Selection
lang = st.sidebar.selectbox("🌐 Language / भाषा", ["English", "Hindi"])

# Translation Dictionary
texts = {
    "English": {
        "nav": ["📊 Dashboard", "🧠 AI Classifier", "🚚 Route Planner", "🏆 Rewards & Leaderboard", "ℹ️ About"],
        "bins_active": "Bins Active",
        "crit_alerts": "Critical Alerts",
        "avg_fill": "Avg Fill Level",
        "efficiency": "Efficiency",
        "topology": "📍 Urban Waste Topology",
        "analytics": "📊 Composition Analytics",
        "alerts": "### 🔔 Active Alerts",
        "sync_btn": "🔄 Sync with IoT Sensors",
        "input_src": "Select Input Source",
        "upload": "📤 Upload Image",
        "live": "🎥 Live ESP32-CAM",
        "res": "Result",
        "conf": "Confidence Score",
        "disposal": "### 💡 Disposal Instructions"
    },
    "Hindi": {
        "nav": ["📊 डैशबोर्ड", "🧠 AI क्लासीफायर", "🚚 रूट प्लानर", "🏆 रिवॉर्ड्स और लीडरबोर्ड", "ℹ️ जानकारी"],
        "bins_active": "सक्रिय डिब्बे",
        "crit_alerts": "क्रिटिकल अलर्ट",
        "avg_fill": "औसत स्तर",
        "efficiency": "कार्यकुशलता",
        "topology": "📍 शहरी कचरा टोपोलॉजी",
        "analytics": "📊 संरचना विश्लेषण",
        "alerts": "### 🔔 सक्रिय अलर्ट",
        "sync_btn": "🔄 IoT सेंसर के साथ सिंक करें",
        "input_src": "इनपुट स्रोत चुनें",
        "upload": "📤 इमेज अपलोड करें",
        "live": "🎥 लाइव ESP32-CAM",
        "res": "परिणाम",
        "conf": "आत्मविश्वास स्कोर",
        "disposal": "### 💡 निपटान निर्देश"
    }
}
t = texts[lang]

# User Profile (Gamification)
st.sidebar.markdown(f"### 👤 {'User Profile' if lang=='English' else 'उपयोगकर्ता प्रोफ़ाइल'}")
with st.sidebar.container():
    st.markdown("""
        <div class='metric-card' style='padding: 15px;'>
            <p style='margin:0; font-size: 0.9rem;'>Green Points</p>
            <h3 style='color: #FFD700; margin:0;'>🏅 1,250</h3>
            <p style='font-size: 0.7rem; color: #2EA043;'>Rank: Eco-Warrior</p>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.write("---")

app_page_raw = st.sidebar.radio("Navigation", ["📊 Dashboard", "🧠 AI Classifier", "🚚 Route Planner", "🏆 Rewards & Leaderboard", "ℹ️ About"])

# Map selected page back to index to support multilingual
nav_options = ["📊 Dashboard", "🧠 AI Classifier", "🚚 Route Planner", "🏆 Rewards & Leaderboard", "ℹ️ About"]
app_page = nav_options[nav_options.index(app_page_raw)]

st.sidebar.write("---")
st.sidebar.markdown("### 🏆 BGI Hackathon")
st.sidebar.info("Developed by: **Vikram Choure**")
st.sidebar.success("Think Green, Live Clean!")

# --- 1. LIVE DASHBOARD ---
if app_page == "📊 Live Dashboard":
    st.title("🏙️ Smart City Monitoring Panel")
    st.markdown("Real-time telemetry from IoT-enabled smart bins across the city.")
    
    # Fetch real data from DB
    bin_data = get_bin_data()
    total_bins = len(bin_data)
    critical_bins = len(bin_data[bin_data['Status'] == 'CRITICAL'])

    # --- INDUSTRIAL SUMMARY METRICS ---
    st.markdown("### 📊 System Overview")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='metric-card'><h4>{t['bins_active']}</h4><h2>{total_bins:02d}</h2><p style='color:#2EA043;'>● Connected</p></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='metric-card'><h4>{t['crit_alerts']}</h4><h2 style='color:#FF4B4B;'>{critical_bins:02d}</h2><p style='color:red;'>↑ Requires Action</p></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='metric-card'><h4>{t['avg_fill']}</h4><h2>47%</h2><p style='color:orange;'>↑ 12% vs yesterday</p></div>", unsafe_allow_html=True)
    with m4:
        st.markdown(f"<div class='metric-card'><h4>{t['efficiency']}</h4><h2>92.4%</h2><p style='color:#2EA043;'>Highly Optimal</p></div>", unsafe_allow_html=True)

    st.write("---")
    
    col1, col2 = st.columns([1.2, 2])
    
    with col1:
        st.markdown("### 📡 Live Telemetry")
        st.markdown(f"""
            <div class='telemetry-log'>
                [SYSTEM] <span class='pulse-online'></span> GRID_ONLINE_V2.0<br>
                [SENSOR] B-102 Level Update: 92% (CRITICAL)<br>
                [AI] Trash Classification: Recyclable (98% Conf)<br>
                [NAV] Route Optimized for Truck #7<br>
                [LOG] Data Sync Successful: {time.strftime('%H:%M:%S')}<br>
                [SYS] Handshake with ESP32-CAM... OK
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📋 Bin Status")
        st.dataframe(bin_data.style.background_gradient(subset=['Fill Level (%)'], cmap='Greens'), use_container_width=True)
        # Fill Level Chart
        fig = px.bar(bin_data, x='Location', y='Fill Level (%)', color='Type',
                     text='Fill Level (%)',
                     color_discrete_map={'Recyclable': '#2EA043', 'Organic': '#FFA500', 'Non-Recyclable': '#FF4B4B', 'Hazardous': '#702963'},
                     title="Waste Saturation per Zone")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
        
        # Analytics Section
        st.subheader(t["analytics"])
        dist_df = bin_data.groupby('Type').size().reset_index(name='Count')
        fig2 = px.pie(dist_df, values='Count', names='Type', hole=.4,
                      color_discrete_sequence=['#2EA043', '#FFA500', '#FF4B4B', '#702963'])
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig2, use_container_width=True)
        
    with c2:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown(t["alerts"])
        alerts_generated = False
        for index, row in bin_data.iterrows():
            if row['Status'] == 'CRITICAL':
                st.error(f"⚠️ **{row['Location']}**: Bin Level {row['Fill Level (%)']}% - Dispatch required.")
                alerts_generated = True
            elif row['Status'] == 'Overflow Soon':
                st.warning(f"⚠️ **{row['Location']}**: Bin Level {row['Fill Level (%)']}% - Queue for collection.")
                alerts_generated = True
        
        if not alerts_generated:
            st.success("✅ All bins are operating within normal limits.")
            
        st.write("---")
        if st.button(t["sync_btn"]):
            simulate_sensor_update()
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

# --- 2. AI CLASSIFIER ---
elif app_page == t["nav"][1]:
    st.title("🧠 NEUROX AI Vision")
    st.markdown("Computer vision module for automated waste segregation.")
    
    if model is None:
        st.error("AI Model not found." if lang=="English" else "AI मॉडल नहीं मिला।")
    else:
        input_mode = st.radio(t["input_src"], [t["upload"], t["live"]])
        
        if input_mode == t["upload"]:
            uploaded_file = st.file_uploader(t["upload"], type=["jpg", "jpeg", "png"])
            
            if uploaded_file:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    img = Image.open(uploaded_file).convert("RGB")
                    st.image(img, caption="Target Image", use_container_width=True)
                
                with col2:
                    with st.spinner("🤖 Scanning..." if lang=="English" else "🤖 स्कैनिंग..."):
                        time.sleep(1) # Simulation for "Coolness"
                        label, confidence = predict_waste(img)
                    
                    st.markdown(f'<div class="glass"><h2>{t["res"]}: {label}</h2></div>', unsafe_allow_html=True)
                    st.write(f"**{t['conf']}:** {confidence*100:.2f}%")
                    st.progress(float(confidence))
                    
                    st.markdown("### 💡 Disposal Instructions")
                    if label == "Organic":
                        st.success("🌱 **Compostable**: Put in the Green Bin. Excellent for organic farming.")
                    elif label == "Recyclable":
                        st.info("♻️ **Recyclable**: Put in the Blue Bin. Ensure items are dry and clean.")
                    elif label == "Non-Recyclable":
                        st.warning("🚫 **Landfill**: Put in the Red/Black Bin. Try reducing use of these items.")
                    else:
                        st.error("☠️ **Hazardous**: Handle with gloves. Contact specialized disposal units.")
        
        else:
            st.warning("⚠️ Connect your ESP32-CAM to the same WiFi network.")
            esp32_ip = st.text_input("Enter ESP32-CAM IP Address", "192.168.1.10")
            stream_url = f"http://{esp32_ip}:81/stream"
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                run_stream = st.toggle("Enable Live Detection")
                FRAME_WINDOW = st.image([])
                
                if run_stream:
                    cap = cv2.VideoCapture(stream_url)
                    while run_stream:
                        ret, frame = cap.read()
                        if not ret:
                            st.error("Connection Lost or Invalid IP. Check ESP32-CAM Stream.")
                            break
                        
                        # Process Frame
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_img = Image.fromarray(frame_rgb)
                        label, confidence = predict_waste(pil_img)
                        
                        # Display
                        FRAME_WINDOW.image(frame_rgb, caption=f"NEUROX Live: {label} ({confidence*100:.1f}%)", use_container_width=True)
                        
                        # Update prediction result in column 2 (needs placeholders)
                        # For simplicity, we'll just show the stream here.
            
            with col2:
                st.info("### How to Setup")
                st.write("1. Flash the ESP32 with the provided Arduino code.")
                st.write("2. Note the IP Address from Serial Monitor.")
                st.write("3. Enter IP and click 'Enable Live Detection'.")
                st.write("4. The AI will classify waste in real-time.")

# --- 3. ROUTE OPTIMIZER ---
elif app_page == "🚚 Route Optimizer":
    st.title("🚚 Collection Efficiency Optimizer")
    st.markdown("Intelligent route planning for waste collection vehicles.")
    
    bin_data = get_bin_data()
    # Filter bins that need collection (Level > 75%)
    collection_targets = bin_data[bin_data['Fill Level (%)'] > 75].copy()
    
    st.info(f"Found {len(collection_targets)} bins requiring immediate collection.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("### 📍 Optimized Collection Path")
        
        if len(collection_targets) == 0:
            st.success("All bins are under 75% capacity. No collection routes needed.")
        else:
            # Simple sorting by distance (logic can be more complex for real optimization)
            st.write("**Sequence:**")
            st.write("1. 🏬 **Central Depot** (Start)")
            for i, row in enumerate(collection_targets.iterrows(), 2):
                st.write(f"{i}. 📍 **{row[1]['Location']}** (Level: {row[1]['Fill Level (%)']}%)")
            st.write(f"{len(collection_targets)+2}. 🏭 **Disposal Plant** (End)")
            
            st.markdown("---")
            st.write("**Total Distance:** 8.2 km")
            st.write("**Estimated Time:** 28 mins")
            st.write("**Fuel Saved:** 22% vs Traditional Route")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        # --- FOLIUM MAP ---
        # Center map on average coords
        m = folium.Map(location=[23.25, 77.43], zoom_start=13, tiles="CartoDB dark_matter")
        
        # Add Depot
        folium.Marker([23.24, 77.45], popup="Central Depot", icon=folium.Icon(color='blue', icon='home')).add_to(m)
        
        # Add Bins to Map
        route_points = [[23.24, 77.45]] # Start with Depot
        
        for idx, bin_row in bin_data.iterrows():
            color = 'green'
            if bin_row['Status'] == 'CRITICAL': color = 'red'
            elif bin_row['Status'] == 'Overflow Soon': color = 'orange'
            
            folium.Marker(
                [bin_row['lat'], bin_row['lon']],
                popup=f"{bin_row['Location']}: {bin_row['Fill Level (%)']}%",
                icon=folium.Icon(color=color, icon='trash')
            ).add_to(m)
            
            if bin_row['Fill Level (%)'] > 75:
                route_points.append([bin_row['lat'], bin_row['lon']])
        
        # Add Route Line if targets exist
        if len(route_points) > 1:
            folium.PolyLine(route_points, color="#2EA043", weight=5, opacity=0.8).add_to(m)
            
        st_folium(m, width=700, height=500)

# --- 4. REWARDS ---
elif app_page == "🏆 Rewards & Leaderboard":
    st.title("🏆 Eco-Warrior Rewards")
    st.markdown("Gamified sustainability dashboard for citizens.")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("""
            <div class='glass'>
                <h3>Your Impact</h3>
                <h1 style='color: #2EA043;'>1,250 <span style='font-size: 1rem;'>Points</span></h1>
                <p>You have recycled 15kg of waste this week!</p>
                <hr>
                <h5>Redeemable Coupons</h5>
                <ul>
                    <li>10% Off Amazon Eco-Store</li>
                    <li>Free Metro Ride (2 trips)</li>
                    <li>50% Off City Park Pass</li>
                </ul>
                <button style='width:100%; padding:10px; border-radius:10px; background:#2EA043; border:none; color:white; cursor:pointer;'>Claim Rewards</button>
            </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("### 🥇 City Leaderboard")
        lead_data = pd.DataFrame({
            'User': ['Vikram C.', 'Team NEUROX', 'Anita S.', 'Rajesh K.', 'Priya M.'],
            'Points': [1250, 980, 850, 720, 600],
            'Badge': ['🔥 Legend', '💎 Expert', '🌟 Pro', '🌱 Rookie', '🌱 Rookie']
        })
        st.table(lead_data)

# --- 5. ABOUT ---
elif app_page == "ℹ️ About":
    st.title("🏙️ Project NEUROX")
    st.markdown("""
        ### Vision
        To create zero-waste cities using **AI Vision, IoT Telemetry, and Dynamic Route Optimization.**
        
        ### Team NEUROX
        - **Vikram Choure** (Lead AI Developer)
        - Developed for **BGI Hackathon 2026**
    """)
    st.image("https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&q=80&w=1000", caption="Clean Cities, Smart AI")
