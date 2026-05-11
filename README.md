# 🏙️ CleanCity AI: Next-Gen Municipal Intelligence Ecosystem
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?style=for-the-badge&logo=tensorflow)](https://tensorflow.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit)](https://streamlit.io)
[![Flutter](https://img.shields.io/badge/Flutter-Mobile_App-02569B?style=for-the-badge&logo=flutter)](https://flutter.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> **Transforming Urban Waste Management into a Predictive, AI-Driven Smart City Operation.**  
> Developed for the BGI Hackathon 2026.

---

## 🚀 The Vision
Traditional waste management is reactive, inefficient, and invisible. **CleanCity AI** transforms this into a proactive, data-driven ecosystem. By combining **Edge AI (Computer Vision)**, **IoT Telemetry**, and **Dynamic Route Optimization**, we create a zero-waste urban topology.

---

## 🔥 Key Features

### 🧠 1. AI Vision Core
*   **Automated Segregation:** Real-time classification of Organic, Recyclable, Non-Recyclable, and Hazardous waste.
*   **Confidence Score:** High-accuracy inference using **MobileNetV2** optimized for edge devices.

### 🛰️ 2. IoT Smart Grid
*   **Multi-Sensor Telemetry:** Live monitoring of Fill Level, Temperature, Gas (CH4) levels, Battery, and Moisture.
*   **Real-time Handshake:** Seamless integration between ESP32-CAM nodes and the central Command Center.

### 🚚 3. Smart Route Optimizer
*   **Dynamic Dispatch:** AI calculates the most efficient collection path based on critical bin priority (>80% fill).
*   **Resource Savings:** Up to 28% reduction in fuel consumption and travel time.
*   **Live Map Centerpiece:** Futuristic "Municipal Command Center" with animated route visualization.

### 🔮 4. Predictive Overflow Analytics
*   **Forecasting Engine:** Predicts exactly when a bin will reach capacity using fill-rate trend analysis.
*   **Early Warning System:** Proactive alerts triggered before overflow occurs.

### 📢 5. Citizen Empowerment
*   **Community Reporting:** Transparent portal for citizens to log waste issues with AI-prioritized resolution.
*   **Gamified Rewards:** "Eco-Warrior" leaderboard to incentivize sustainable waste disposal.

---

## 🏗️ System Architecture
CleanCity AI follows a **Modular Clean Architecture** for maximum scalability:

```text
CleanCityAI/
├── 🧠 ai_engine/           # Vision & Classification Modules
├── 📈 analytics_engine/    # Predictive Forecasting Logic
├── 🚨 alerts_engine/       # Notification & Alert Gateway
├── 🚚 route_engine/        # AI-based Path Optimization
├── 🖥️ backend_dashboard/   # Streamlit Command Center
├── 📱 mobile_app/          # Flutter Driver/Citizen Application
└── 📡 iot_gateway/         # Hardware Firmware & Simulators
```

---

## 🛠️ Technology Stack
*   **Frontend:** Streamlit (Admin), Flutter (Mobile)
*   **Backend:** Python 3.10, FastAPI (Mobile API)
*   **AI/ML:** TensorFlow, MobileNetV2, NumPy, Scikit-learn
*   **Database:** SQLite (Demo Ready) / PostgreSQL
*   **Mapping:** Folium, OpenStreetMap, OSRM Engine
*   **IoT:** ESP32-CAM, Ultrasonic (SR04), MQ4 Gas Sensor

---

## 🏁 Getting Started

### 1. Prerequisites
*   Python 3.10 or higher
*   Flutter SDK (for mobile)
*   VS Code / PyCharm

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/YourUsername/CleanCityAI.git

# Navigate to project
cd CleanCityAI

# Install dependencies
pip install -r backend_dashboard/requirements.txt
```

### 3. Run the Command Center
```bash
streamlit run backend_dashboard/app.py
```

---

## 🗺️ Roadmap & Future Scope
- [ ] **Edge AI Integration:** Deploying TFLite models directly on ESP32-S3.
- [ ] **Blockchain Incentives:** Transparent reward tokens for waste segregation.
- [ ] **Fleet Management:** Real-time GPS tracking for garbage trucks.
- [ ] **Multilingual Voice Support:** For field staff and citizens.

---

## 👥 The Team: NEUROX
*   **Vikram Choure** - Lead AI Systems Architect & Full-Stack Developer
*   **Team Mission:** Building a cleaner, smarter, and sustainable future.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
**CleanCity AI** - *Municipal Intelligence, Redefined.* 🏙️💎
