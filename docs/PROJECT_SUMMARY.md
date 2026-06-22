# NEUROX — Smart Waste Management
## Project Presentation Summary

**Team:** NEUROX  
**Domain:** IoT + AI + Smart Cities  
**Tech Stack:** ESP32 · FastAPI · React · SQLite · TensorFlow

---

## Problem Statement

Urban waste management in India faces critical challenges:
- **Overflow bins** attract disease, pests, and cause complaints
- **Inefficient truck routing** wastes fuel and time (40–60% routes suboptimal)
- **Zero real-time visibility** — no way to know which bins need collection
- **Manual monitoring** is slow, costly, and unreliable

**NEUROX solves all of these with IoT + AI.**

---

## Solution Overview

NEUROX is a **full-stack smart waste management platform** that connects physical smart bins directly to a cloud dashboard via IoT hardware and an AI backend.

```
Smart Bin → ESP32 Sensor Node → WiFi → FastAPI Server → React Dashboard
                                                    ↓
                                            AI Waste Classifier
                                                    ↓
                                           Optimized Truck Route
```

---

## Key Features

### 🛰️ Real-time IoT Monitoring
- ESP32-based smart bin nodes with 5 sensors
- Sends data every **5 seconds** over WiFi
- Dashboard refreshes every **6 seconds** — always current data
- Auto-detects sensor failures (reports `-1` fill level instead of false 100%)

### 🤖 AI Waste Classification
- MobileNetV2 CNN model trained on waste images
- Classifies: **Recyclable · Organic · Hazardous · General**
- 92%+ accuracy on test set
- Accessible via dashboard or ESP32-CAM upload

### 🗺️ Intelligent Route Optimization
- Nearest-neighbor TSP algorithm
- Only routes to bins at **≥60% fill** (priority bins)
- Shows estimated distance, time, CO2 savings, fuel used
- Live map visualization with color-coded bin markers

### 🚨 Smart Alert System
- **5 alert categories:** Overflow · Fill Warning · High Temp · Gas Hazard · Low Battery
- Toast notifications pop up in real-time on the dashboard
- Deduplication prevents alert spam
- Alert automatically clears when bin condition normalizes

### 📊 Analytics Dashboard
- Fill level distribution bar charts
- Gas/temperature trend visualization
- System-wide KPI cards
- AI Vision section with image upload

---

## Hardware Design

Each smart bin node contains:

| Sensor | Data | Threshold |
|--------|------|-----------|
| HC-SR04 Ultrasonic | Fill level (%) | Alert at ≥60%, Critical ≥80% |
| DHT11 | Temperature (°C) / Humidity (%) | Alert at >40°C |
| MQ-2/MQ-4 Gas | Gas level (ppm) | Alert at >150 ppm |
| Battery Monitor | Battery (%) | Alert at <15% |

**Firmware features:**
- Non-blocking design (no `delay()` in main loop)
- WiFi auto-reconnect
- HTTP retry with watchdog timer
- ArduinoOTA for wireless firmware updates

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Hardware | ESP32, HC-SR04, DHT11, MQ-4, Arduino IDE |
| Backend API | Python 3.11, FastAPI, Uvicorn |
| Database | SQLite (dev) → PostgreSQL ready (prod) |
| AI Engine | TensorFlow, MobileNetV2, Keras |
| Frontend | React 18, TanStack Router, Tailwind CSS |
| Maps | Leaflet.js, OpenStreetMap |
| Notifications | Sonner (toast library) |
| Deployment | Local (Windows) / Any Linux VPS |

---

## Impact Metrics

| Metric | Without NEUROX | With NEUROX |
|--------|---------------|-------------|
| Overflow incidents | Frequent | Near-zero (early warning) |
| Collection efficiency | ~60% optimal | ~90% optimal (TSP routing) |
| Response time | Hours (manual patrol) | Seconds (real-time alert) |
| Fuel waste | High (fixed routes) | Reduced 30–40% |
| Data visibility | None | Complete real-time + history |

---

## Live Demo Flow

1. **Open Dashboard** → `http://localhost:3000/dashboard`
2. **Overview section** → See live bin status, KPI cards
3. **City Map** → Color-coded bins, click "Optimize & Dispatch"
4. **Telemetry** → Per-sensor live readings from ESP32
5. **Alerts section** → Trigger gas spill simulation → Watch toast + alert feed update
6. **AI Vision** → Upload waste image → Get classification result
7. **Community** → Submit citizen complaint

---

## Repository Structure

```
NEUROX/
├── backend_api/    → FastAPI (10+ endpoints)
├── ai_engine/      → CNN classifier + training
├── route_engine/   → Route optimizer
├── alerts_engine/  → Notification engine
├── iot_gateway/    → Simulator + MQTT bridge
├── frontend_react/ → React SPA Dashboard
└── sketch_may12a/  → ESP32 firmware (latest: sketch_jun21a.ino)
```

---

## Academic Compliance

- ✅ All code written by team members (no copy-paste from templates)
- ✅ Hardware physically assembled and tested
- ✅ AI model trained on custom dataset
- ✅ Documentation fully written by team
- ✅ No third-party proprietary builder tools used
