# API Guide — NEUROX Smart Waste Management

This document provides complete API usage examples using **PowerShell** (Windows) and `curl` (Linux/Mac).

Base URL: `http://localhost:8000`

---

## 🏥 Health Check

### `GET /health`

Check the operational status of all system components.

```powershell
Invoke-RestMethod http://localhost:8000/health
```

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "Operational",
  "database": "Connected",
  "ai_engine": "Ready",
  "ai_backend": "keras",
  "iot_gateway": "Active",
  "device_auth_required": false,
  "admin_routes_enabled": false
}
```

---

## 🗑️ Bin Management

### `POST /bins` — Register Single Bin

```powershell
$body = @{
    id         = 1
    location   = "Main Gate"
    lat        = 23.2599
    lon        = 77.4126
    zone       = "FIELD"
    waste_type = "Mixed"
    fill_level = 0
    gas_level  = 0
    temp       = 25
    battery    = 100
    moisture   = 0
    status     = "NORMAL"
    tenant_id  = "default"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/bins -Method POST -Body $body -ContentType "application/json"
```

**Response:**
```json
{
  "status": "registered",
  "bin_id": 1,
  "tenant_id": "default"
}
```

---

### `POST /bins/bulk` — Register Multiple Bins

```powershell
$body = @{
    bins = @(
        @{ id=1; location="Gate A"; lat=23.26; lon=77.41; zone="FIELD" },
        @{ id=2; location="Gate B"; lat=23.25; lon=77.42; zone="FIELD" },
        @{ id=3; location="Canteen"; lat=23.24; lon=77.43; zone="INDOOR" }
    )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri http://localhost:8000/bins/bulk -Method POST -Body $body -ContentType "application/json"
```

---

### `POST /bins/import-csv` — Import Bins from CSV

CSV format (`bins.csv`):
```csv
id,location,lat,lon,zone,waste_type,fill_level,gas_level,temp,battery,moisture,status,tenant_id
1,Main Gate,23.2599,77.4126,FIELD,Mixed,0,0,25,100,0,NORMAL,default
2,Library,23.2601,77.4130,INDOOR,Recyclable,0,0,25,100,0,NORMAL,default
```

```powershell
$form = @{ file = Get-Item "bins.csv" }
Invoke-RestMethod -Uri http://localhost:8000/bins/import-csv -Method POST -Form $form
```

---

## 📡 Telemetry

### `GET /telemetry` — Get All Bin Data

```powershell
Invoke-RestMethod http://localhost:8000/telemetry
```

### `GET /telemetry?tenant_id=campus_a` — Filter by Tenant

```powershell
Invoke-RestMethod "http://localhost:8000/telemetry?tenant_id=campus_a"
```

**Response (single bin):**
```json
{
  "id": 1,
  "location": "Main Gate",
  "fill_level": 45,
  "type": "Mixed",
  "status": "Real",
  "lat": 23.2599,
  "lon": 77.4126,
  "temp": 28.5,
  "gas_level": 58,
  "battery": 87,
  "moisture": 40,
  "zone": "FIELD",
  "tenant_id": "default",
  "last_update": "2026-06-22T10:30:00.000000"
}
```

---

### `POST /iot/update` — Hardware Telemetry from ESP32

This endpoint is called by the ESP32 firmware every 5 seconds.

```powershell
$body = @{
    bin_id      = 1
    location    = "Smart bin node 1"
    latitude    = 23.2599
    longitude   = 77.4126
    zone        = "FIELD"
    fill_level  = 45
    gas_level   = 58
    temperature = 28.5
    humidity    = 40.6
    battery     = 87
    sensor_ok   = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/iot/update -Method POST -Body $body -ContentType "application/json"
```

**Response:**
```json
{
  "status": "Hardware Data Synchronized",
  "bin_id": 1,
  "anomaly_flags": null
}
```

> **Auto-registration:** If `bin_id` does not exist in the database but `location`, `latitude`, `longitude` are provided — the bin is automatically registered on first contact.

> **Anomaly detection:** If fill level jumps by ≥ 30% from the previous reading, `anomaly_flags` will return `"SUDDEN_FILL_JUMP"`.

---

### `POST /bins/reset` — Reset Bins After Collection

Call this after a truck empties specific bins.

```powershell
$body = @{ bin_ids = @(1, 2, 3) } | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/bins/reset -Method POST -Body $body -ContentType "application/json"
```

---

## 🤖 AI Vision

### `POST /predict` — Classify Waste from Image

```powershell
$form = @{ file = Get-Item "waste_photo.jpg" }
Invoke-RestMethod -Uri http://localhost:8000/predict -Method POST -Form $form
```

```bash
curl -X POST http://localhost:8000/predict \
     -F "file=@waste_photo.jpg"
```

**Response:**
```json
{
  "label": "Recyclable",
  "confidence": 0.92,
  "guidance": "Place in the blue recycling bin. Ensure it is clean and dry.",
  "inference_time": "0.38s"
}
```

> Requires `ai_engine/models/waste_model.h5` to be present. Returns `503` if model is missing.

---

## 🗺️ Route Optimization

### `GET /route` — Get Optimized Truck Route

```powershell
Invoke-RestMethod http://localhost:8000/route
```

**Response:**
```json
{
  "route": [
    { "bin_id": 3, "location": "Library", "fill": 85, "lat": 23.2601, "lon": 77.4130 },
    { "bin_id": 1, "location": "Main Gate", "fill": 75, "lat": 23.2599, "lon": 77.4126 }
  ],
  "metrics": {
    "distance": "2.4 km",
    "time": "~12 min",
    "co2": "0.48 kg",
    "fuel": "0.24 L"
  }
}
```

Only bins with fill level ≥ 60% are included in the route.

---

## 📣 Citizen Complaints

### `POST /complaints` — Submit Complaint

```powershell
$body = @{
    user_name = "Ramesh Kumar"
    location  = "Sector 5 Market"
    type      = "Overflowing bin"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/complaints -Method POST -Body $body -ContentType "application/json"
```

### `GET /complaints` — Get Recent Complaints

```powershell
Invoke-RestMethod "http://localhost:8000/complaints?limit=10"
```

---

## 🔑 Authentication

If `DEVICE_INGEST_SECRET` is set as an environment variable, protected endpoints require the `X-Device-Token` header:

```powershell
$headers = @{ "X-Device-Token" = "your_secret_here" }
Invoke-RestMethod -Uri http://localhost:8000/bins -Method POST -Headers $headers -Body $body -ContentType "application/json"
```

If `ADMIN_API_SECRET` is set, admin endpoints require the `X-Admin-Token` header:

```powershell
$headers = @{ "X-Admin-Token" = "your_admin_secret" }
Invoke-RestMethod -Uri "http://localhost:8000/admin/prune-sensor-logs?days=30" -Method POST -Headers $headers
```

---

## ⚙️ Admin Endpoints

### `POST /admin/prune-sensor-logs?days=N`

Delete sensor log records older than N days (minimum 7, maximum 3650).

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/admin/prune-sensor-logs?days=30" -Method POST
```

### `POST /admin/rollup-sensor-logs-hourly`

Aggregate raw sensor logs into hourly summaries to save database space.

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/admin/rollup-sensor-logs-hourly?lookback_days=14" -Method POST
```

---

## 🔍 Interactive API Documentation

FastAPI automatically generates interactive API docs:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
