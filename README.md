# NEUROX — AI Smart Waste Management System

> **Real-time IoT + AI powered smart waste management platform** built with ESP32, FastAPI, and React.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)](https://react.dev)
[![ESP32](https://img.shields.io/badge/Hardware-ESP32%20%2F%20Arduino-red?logo=arduino)](https://www.espressif.com)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NEUROX Platform                              │
│                                                                     │
│  ┌─────────────┐    HTTP/JSON    ┌──────────────┐                  │
│  │  ESP32 IoT  │ ─────────────► │  FastAPI     │                  │
│  │  Smart Bin  │  POST /iot/    │  Backend     │ ◄── SQLite DB    │
│  │  Node       │  update        │  Port: 8000  │                  │
│  └─────────────┘                └──────┬───────┘                  │
│                                        │  REST API                 │
│  ┌─────────────┐                ┌──────▼───────┐                  │
│  │ ESP32-CAM   │ ──────────────►│  React SPA   │                  │
│  │ Vision Node │  /predict      │  Dashboard   │                  │
│  └─────────────┘                │  Port: 3000  │                  │
│                                 └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
```

**Data Flow:**
1. ESP32 collects sensor data (ultrasonic fill level, DHT11 temp/humidity, MQ gas, battery)
2. ESP32 POSTs telemetry to FastAPI `/iot/update` every **5 seconds**
3. FastAPI validates, stores in SQLite, detects anomalies
4. React dashboard polls `/telemetry` every **6 seconds** — always fresh data
5. AI vision module (`/predict`) classifies waste from ESP32-CAM uploads
6. Route engine computes optimal truck dispatch paths

---

## 📁 Project Structure

```
Smart_Waste_Management_main/
│
├── backend_api/                 # FastAPI backend (REST API + IoT gateway)
│   ├── main.py                  # All API routes (bins, telemetry, AI, routing, complaints)
│   ├── settings.py              # Environment config (secrets, thresholds)
│   ├── deps_auth.py             # Auth middleware (device token, admin secret)
│   ├── bin_validation.py        # Input validation helpers
│   ├── schemas/
│   │   └── api_models.py        # Pydantic request/response models
│   └── database/
│       └── manager.py           # SQLite connection manager
│
├── ai_engine/                   # Waste classification AI (CNN / TensorFlow)
│   ├── classifier.py            # Model loader + predict() function
│   ├── train_model.py           # Training script (MobileNetV2 transfer learning)
│   └── models/                  # Trained model files (.h5)
│
├── route_engine/                # Truck route optimization
│   └── optimizer.py             # Nearest-neighbor TSP for priority bins
│
├── alerts_engine/               # Server-side alert notifier
│   └── notifier.py              # Threshold checking + notification logic
│
├── analytics_engine/            # (Future) Analytics aggregation
│
├── iot_gateway/                 # IoT simulator + MQTT bridge
│   ├── sensor_simulator.py      # Soft-simulation for bins without hardware
│   └── mqtt_bridge.py           # Optional MQTT → REST bridge
│
├── frontend_react/              # React SPA Dashboard (NEUROX UI)
│   ├── src/
│   │   ├── routes/
│   │   │   ├── dashboard.tsx    # Main control center (telemetry, alerts, map, AI)
│   │   │   ├── index.tsx        # Landing page
│   │   │   ├── about.tsx        # Team / about page
│   │   │   ├── architecture.tsx # System architecture page
│   │   │   ├── solutions.tsx    # Solutions page
│   │   │   ├── use-cases.tsx    # Use cases page
│   │   │   └── contact.tsx      # Contact page
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   │   └── CityMap.tsx  # Leaflet live bin map
│   │   │   └── site/
│   │   │       ├── Header.tsx   # Navigation header
│   │   │       └── Footer.tsx   # Site footer
│   │   └── styles.css           # Global design tokens + Tailwind
│   ├── vite.config.ts           # Vite build + /api proxy to port 8000
│   └── package.json
│
├── sketch_may12a/               # Arduino / ESP32 firmware
│   ├── sketch_may12a.ino        # Legacy reference firmware
│   └── sketch_jun21a/
│       └── sketch_jun21a.ino    # ✅ LATEST — production firmware with OTA + WDT
│
├── dataset/                     # Training images for AI model
├── docs/                        # Extended documentation
│   ├── FEATURES.md              # Complete feature capability matrix
│   └── DEPLOY_POSTGRES.md       # PostgreSQL migration guide
├── scripts/
│   └── start_fullstack.bat      # One-click Windows launcher
├── requirements.txt             # Python dependencies
├── smart_bins.db                # SQLite database (auto-created)
└── test_api.py                  # API smoke tests
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.11+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Git | Any | [git-scm.com](https://git-scm.com) |

### One-Click Launch (Windows)

```powershell
.\scripts\start_fullstack.bat
```

This activates the virtual environment, launches FastAPI on port 8000, starts the React dashboard on port 3000, and opens the browser automatically.

---

### Manual Setup

#### 1. Clone & Setup Python Environment

```powershell
git clone <repo-url>
cd Smart_Waste_Management_main

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### 2. Start FastAPI Backend (Port 8000)

```powershell
python -m uvicorn backend_api.main:app --host 0.0.0.0 --port 8000 --reload
```

✅ API live at: `http://localhost:8000`
✅ Interactive Swagger docs: `http://localhost:8000/docs`

#### 3. Start React Dashboard (Port 3000)

```powershell
cd frontend_react
npm install
npm run dev -- --port 3000
```

✅ Dashboard live at: `http://localhost:3000/dashboard`

---

## 📡 API Reference

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | System health check (AI, DB, IoT status) | None |
| `GET` | `/telemetry` | All bin telemetry data | None |
| `POST` | `/bins` | Register a single bin | Device Token |
| `POST` | `/bins/bulk` | Register multiple bins (JSON array) | Device Token |
| `POST` | `/bins/import-csv` | Bulk import from CSV file | Device Token |
| `POST` | `/bins/reset` | Reset fill levels after truck collection | None |
| `POST` | `/iot/update` | Receive hardware telemetry from ESP32 | Device Token |
| `POST` | `/predict` | AI waste classification (image upload) | None |
| `GET` | `/route` | Get optimized truck collection route | None |
| `POST` | `/complaints` | Submit citizen waste complaint | None |
| `GET` | `/complaints` | Get recent citizen complaints | None |
| `POST` | `/admin/prune-sensor-logs` | Delete old sensor logs | Admin Token |
| `POST` | `/admin/rollup-sensor-logs-hourly` | Aggregate sensor logs by hour | Admin Token |

### IoT Update Payload (ESP32 → Server)

```json
{
  "bin_id": 1,
  "location": "Smart bin node 1",
  "latitude": 23.2599,
  "longitude": 77.4126,
  "zone": "FIELD",
  "fill_level": 45,
  "gas_level": 58,
  "temperature": 28.5,
  "humidity": 40.6,
  "battery": 87,
  "sensor_ok": true
}
```

**Response:**
```json
{
  "status": "Hardware Data Synchronized",
  "bin_id": 1,
  "anomaly_flags": null
}
```

> If `fill_level` jumps by more than `ANOMALY_JUMP_THRESHOLD` (default: 30%), `anomaly_flags` will be `"SUDDEN_FILL_JUMP"`.

---

## 🔧 ESP32 Hardware Setup

### Firmware: `sketch_may12a/sketch_jun21a/sketch_jun21a.ino`

This is the **latest production firmware** for the ESP32 bin node.

#### Pin Configuration

| Pin | GPIO | Sensor |
|-----|------|--------|
| TRIG_PIN | GPIO 14 | HC-SR04 Ultrasonic Trigger |
| ECHO_PIN | GPIO 15 | HC-SR04 Ultrasonic Echo |
| GAS_PIN | GPIO 34 | MQ-2/MQ-4 Gas Sensor (ADC) |
| BATTERY_PIN | GPIO 35 | Battery Voltage Divider (ADC) |
| DHTPIN | GPIO 12 | DHT11 Temperature/Humidity |

#### Before Flashing — Edit These Values

```cpp
// WiFi credentials
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Server URL (replace with your machine's local IP)
const char* serverUrl = "http://192.168.X.X:8000/iot/update";

// Device auth token (must match DEVICE_INGEST_SECRET on server)
const char* deviceToken = "YOUR_SECRET_TOKEN";

// Bin identity (change per physical device)
const int   BIN_ID       = 1;
const char* BIN_LOCATION = "Main Gate Bin";
const float BIN_LATITUDE = 23.2599;
const float BIN_LONGITUDE= 77.4126;
const char* BIN_ZONE     = "FIELD";

// Bin physical height in cm (for fill level calculation)
const int BIN_HEIGHT_CM = 30;
```

#### Firmware Features

| Feature | Detail |
|---------|--------|
| **Non-blocking loop** | Uses `millis()` timer — never uses `delay()` in main loop |
| **Send interval** | `SEND_INTERVAL_MS = 5000` (every 5 seconds) |
| **Ultrasonic timeout** | 30ms `pulseIn` timeout prevents hang on sensor failure |
| **Sensor error handling** | Fill = `-1` on ultrasonic failure (server ignores false readings) |
| **HTTP retry** | 2 attempts with 500ms delay between failures |
| **WiFi auto-reconnect** | Detects disconnect and reconnects in main loop |
| **OTA Update** | ArduinoOTA enabled — flash wirelessly over LAN |
| **Watchdog Timer** | 60s WDT — auto-resets on hang |
| **Battery monitoring** | ADC voltage mapped to 0–100% |

#### Required Arduino Libraries

Install via Arduino IDE → Library Manager:
- `DHT sensor library` by Adafruit
- `ArduinoJson` by Benoit Blanchon
- `ArduinoOTA` (built-in with ESP32 core)

#### Arduino Board Settings

```
Board      : ESP32 Dev Module
Upload Speed: 115200
Partition  : Default 4MB with spiffs
```

---

## 🤖 AI Vision Module

The AI engine classifies waste images uploaded via the dashboard or ESP32-CAM.

### Setup (Optional)

1. Train the model or place pre-trained weights:
   ```
   ai_engine/models/waste_model.h5
   ```

2. Install TensorFlow:
   ```powershell
   pip install tensorflow==2.15.0
   # Windows: also run if import fails:
   winget install Microsoft.VCRedist.2015+.x64
   ```

3. Train from scratch using your dataset:
   ```powershell
   python ai_engine/train_model.py
   ```

### Waste Categories
- `Recyclable` — plastic, metal, glass, paper
- `Organic` — food waste, garden waste
- `Hazardous` — batteries, chemicals, e-waste
- `General` — mixed/other waste

---

## 📊 Dashboard Features

The NEUROX React dashboard (`http://localhost:3000/dashboard`) provides:

| Section | Features |
|---------|----------|
| **Overview** | KPI cards, network snapshot, live event stream, IoT event simulator |
| **City Map** | Leaflet map with real-time bin markers, fill color coding, route visualization |
| **Telemetry** | Per-bin sensor cards (fill, temp, gas, battery, humidity) |
| **Alerts** | 5-category alert board, live alert feed, dispatch button |
| **Analytics** | Fill/gas distribution bar charts, multi-metric line charts |
| **AI Vision** | Image upload → waste classification with confidence score |
| **Community** | Citizen complaint submission and live feed |

### Alert Thresholds

| Alert Type | Threshold | Severity |
|-----------|-----------|---------|
| Overflow Risk | Fill ≥ 80% | 🔴 Critical |
| Fill Warning | Fill 60–79% | 🟡 Warning |
| High Temperature | Temp > 40°C | 🟡 Warning |
| Gas Hazard | Gas > 150 ppm | 🔴 Critical |
| Low Battery | Battery < 15% | 🟡 Warning |

---

## 🌐 Environment Variables

Create a `.env` file in the project root (optional — all values have defaults):

```env
# Security — leave empty to disable auth
DEVICE_INGEST_SECRET=your_iot_device_secret
ADMIN_API_SECRET=your_admin_secret

# Defaults
DEFAULT_TENANT_ID=default
ANOMALY_JUMP_THRESHOLD=30

# MQTT Bridge (optional)
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC_TELEMETRY=cleancity/bins/#
CLEANCITY_API_URL=http://localhost:8000
```

---

## 🧪 Testing

### API Smoke Test

```powershell
python test_api.py
```

### Manual API Test (PowerShell)

```powershell
# Health check
Invoke-RestMethod http://localhost:8000/health

# Get all bins
Invoke-RestMethod http://localhost:8000/telemetry

# Send test telemetry
$body = @{
    bin_id    = 1
    location  = "Test Bin"
    latitude  = 23.2599
    longitude = 77.4126
    zone      = "TEST"
    fill_level = 75
    gas_level  = 60
    temperature= 29.5
    humidity   = 45.0
    battery    = 85
    sensor_ok  = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/iot/update -Method POST -Body $body -ContentType "application/json"
```

---

## 👥 Team — NEUROX

| Role | Contribution |
|------|-------------|
| Hardware Lead | ESP32 circuit design, sensor integration, firmware development |
| Backend Lead | FastAPI design, database schema, IoT gateway, anomaly detection |
| AI Lead | CNN model architecture, dataset curation, TensorFlow training pipeline |
| Frontend Lead | React dashboard, real-time telemetry UI, alert system, map integration |

---

## 📄 Additional Documentation

| Document | Description |
|----------|-------------|
| [`docs/FEATURES.md`](docs/FEATURES.md) | Complete feature capability matrix |
| [`docs/DEPLOY_POSTGRES.md`](docs/DEPLOY_POSTGRES.md) | PostgreSQL migration guide for production |
| [`docs/API_GUIDE.md`](docs/API_GUIDE.md) | Detailed API usage with curl examples |
| [`docs/HARDWARE_WIRING.md`](docs/HARDWARE_WIRING.md) | Full wiring diagrams and circuit notes |

---

## 📜 License

This project was developed as an academic project by Team NEUROX.
