# NEUROX — Setup & Deployment Guide

## Quick Checklist

Before presenting or demonstrating the project, verify each item:

- [ ] Python 3.11+ installed (`python --version`)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] `.venv` virtual environment created
- [ ] All Python packages installed (`pip install -r requirements.txt`)
- [ ] React packages installed (`cd frontend_react && npm install`)
- [ ] FastAPI backend starts without errors (`python -m uvicorn ...`)
- [ ] React dashboard loads at `http://localhost:3000`
- [ ] `http://localhost:8000/health` returns `"status": "Operational"`
- [ ] At least one bin visible in dashboard
- [ ] (Optional) ESP32 flashed and on same WiFi as server

---

## Step-by-Step Setup

### Step 1 — Create Python Virtual Environment

```powershell
# From project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` prefix in your terminal.

### Step 2 — Install Python Dependencies

```powershell
pip install -r requirements.txt
```

> If TensorFlow is needed for AI vision:
> ```powershell
> pip install tensorflow==2.15.0
> # If msvcp140_1.dll error on Windows:
> winget install Microsoft.VCRedist.2015+.x64
> ```

### Step 3 — Start FastAPI Backend

```powershell
python -m uvicorn backend_api.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify at: `http://localhost:8000/health`

Expected output:
```json
{
  "status": "Operational",
  "database": "Connected",
  "ai_engine": "No model file",
  "iot_gateway": "Active"
}
```

### Step 4 — Start React Dashboard

Open a **new terminal window**:

```powershell
cd frontend_react
npm install
npm run dev -- --port 3000
```

Dashboard opens at: `http://localhost:3000`

### Step 5 — Flash ESP32 (Hardware Demo)

1. Open `sketch_may12a/sketch_jun21a/sketch_jun21a.ino` in Arduino IDE
2. Edit WiFi credentials and server IP:
   ```cpp
   const char* ssid = "YOUR_WIFI";
   const char* password = "YOUR_PASSWORD";
   const char* serverUrl = "http://YOUR_PC_IP:8000/iot/update";
   ```
3. Select: Board → **ESP32 Dev Module**
4. Select correct COM Port
5. Upload
6. Open Serial Monitor (115200 baud) to verify connection

---

## Adding Simulated Bins (No Hardware)

If no ESP32 is available, add test bins via API:

```powershell
# Activate venv first
.\.venv\Scripts\Activate.ps1

# Add 3 test bins
$bins = @{
    bins = @(
        @{id=1; location="Main Gate Bin"; lat=23.2599; lon=77.4126; zone="FIELD"; fill_level=72; gas_level=45; temp=29; battery=80; moisture=40; status="NORMAL"; waste_type="Mixed"; tenant_id="default"},
        @{id=2; location="Library Entrance"; lat=23.2610; lon=77.4140; zone="INDOOR"; fill_level=85; gas_level=30; temp=27; battery=60; moisture=35; status="NORMAL"; waste_type="Recyclable"; tenant_id="default"},
        @{id=3; location="Sports Complex"; lat=23.2580; lon=77.4110; zone="FIELD"; fill_level=35; gas_level=20; temp=31; battery=90; moisture=30; status="NORMAL"; waste_type="Organic"; tenant_id="default"}
    )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri http://localhost:8000/bins/bulk -Method POST -Body $bins -ContentType "application/json"
```

---

## Environment Variables (Optional)

Create `.env` in project root to configure security and behavior:

```env
# Device token — ESP32 must send this in X-Device-Token header
DEVICE_INGEST_SECRET=neurox2024secret

# Admin token — for prune/rollup endpoints
ADMIN_API_SECRET=admin2024secret

# Default tenant name
DEFAULT_TENANT_ID=default

# Fill jump to trigger anomaly flag (%)
ANOMALY_JUMP_THRESHOLD=30
```

---

## Common Errors & Fixes

### ❌ `ModuleNotFoundError: No module named 'fastapi'`

```powershell
# Make sure venv is active
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ❌ `Port 8000 already in use`

```powershell
# Find what's using it
netstat -ano | findstr :8000
# Kill the process (replace PID)
taskkill /PID <PID> /F
```

### ❌ `EACCES: permission denied` on npm

```powershell
# Run as Administrator or use:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ Dashboard shows no bins

1. Check FastAPI is running: `http://localhost:8000/health`
2. Add bins manually using the PowerShell commands above
3. Check browser console for CORS or network errors

### ❌ ESP32 shows `Send failed (-1)`

1. Verify both PC and ESP32 are on **same WiFi** (2.4GHz)
2. Get your PC's IP: `ipconfig` → Look for `IPv4 Address`
3. Update `serverUrl` in firmware and re-flash

### ❌ AI Vision returns 503

Place trained model at `ai_engine/models/waste_model.h5` and restart backend.

---

## Production Build (For Submission / Demo)

```powershell
cd frontend_react
npm run build
```

Built files go to `frontend_react/dist/`. The FastAPI backend can serve these static files directly.

---

## Useful URLs

| URL | Purpose |
|-----|---------|
| `http://localhost:3000` | NEUROX Landing Page |
| `http://localhost:3000/dashboard` | Live Control Dashboard |
| `http://localhost:8000` | FastAPI Status Page |
| `http://localhost:8000/docs` | Swagger Interactive API Docs |
| `http://localhost:8000/health` | System Health JSON |
| `http://localhost:8000/telemetry` | Raw Bin Data JSON |
