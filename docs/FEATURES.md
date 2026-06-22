# NEUROX — Feature Capability Matrix

> Complete list of all implemented features across hardware, backend, AI, and frontend layers.

---

## 🛰️ IoT Hardware Layer

| Feature | Status | Notes |
|---------|--------|-------|
| Ultrasonic fill level sensing | ✅ Done | HC-SR04 with 30ms timeout, -1 on failure |
| DHT11 temperature & humidity | ✅ Done | Validates NaN, reports 0 on error |
| MQ gas sensor (analog) | ✅ Done | Mapped 0–4095 ADC → 0–100 ppm scale |
| Battery voltage monitoring | ✅ Done | ADC voltage divider → 0–100% |
| Non-blocking loop (`millis()`) | ✅ Done | No `delay()` in main loop |
| WiFi auto-reconnect | ✅ Done | Detects drop, reconnects automatically |
| HTTP retry on failure | ✅ Done | 2 attempts, 500ms delay |
| ArduinoOTA wireless flashing | ✅ Done | Enabled on same LAN |
| Watchdog Timer (60s) | ✅ Done | Prevents infinite hang |
| Auto-registration on first sync | ✅ Done | New bin_id + location → auto registers |
| Sensor error reporting | ✅ Done | `fill_level = -1` on ultrasonic failure |
| JSON serialization (ArduinoJson) | ✅ Done | Safe, no manual string concat |

---

## 🖥️ Backend API Layer (FastAPI)

### Bin Management

| Feature | Endpoint | Status |
|---------|----------|--------|
| Register single bin | `POST /bins` | ✅ Done |
| Register multiple bins | `POST /bins/bulk` | ✅ Done |
| Import bins from CSV | `POST /bins/import-csv` | ✅ Done |
| Get all telemetry | `GET /telemetry` | ✅ Done |
| Filter by tenant | `GET /telemetry?tenant_id=` | ✅ Done |
| Update bin from hardware | `POST /iot/update` | ✅ Done |
| Auto-register unknown bins | `POST /iot/update` | ✅ Done |
| Reset bins after collection | `POST /bins/reset` | ✅ Done |

### Anomaly Detection

| Feature | Status | Notes |
|---------|--------|-------|
| Sudden fill jump detection | ✅ Done | `ANOMALY_JUMP_THRESHOLD` (default 30%) |
| Sensor failure flag | ✅ Done | `sensor_ok: false` ignored for fill |
| Anomaly flag in response | ✅ Done | `"anomaly_flags": "SUDDEN_FILL_JUMP"` |

### AI Vision

| Feature | Endpoint | Status |
|---------|----------|--------|
| Waste classification (image) | `POST /predict` | ✅ Done |
| Confidence score | `POST /predict` | ✅ Done |
| Disposal guidance text | `POST /predict` | ✅ Done |
| Inference time reporting | `POST /predict` | ✅ Done |
| Graceful offline mode | `POST /predict` | ✅ Done (503 when model missing) |

### Route Optimization

| Feature | Endpoint | Status |
|---------|----------|--------|
| Nearest-neighbor TSP | `GET /route` | ✅ Done |
| Priority bin filtering (≥60%) | `GET /route` | ✅ Done |
| Distance + ETA + CO2 metrics | `GET /route` | ✅ Done |
| Tenant-filtered routing | `GET /route?tenant_id=` | ✅ Done |

### Community

| Feature | Endpoint | Status |
|---------|----------|--------|
| Submit citizen complaint | `POST /complaints` | ✅ Done |
| Get complaints list | `GET /complaints?limit=` | ✅ Done |

### Administration

| Feature | Endpoint | Status |
|---------|----------|--------|
| Prune old sensor logs | `POST /admin/prune-sensor-logs` | ✅ Done |
| Rollup to hourly summary | `POST /admin/rollup-sensor-logs-hourly` | ✅ Done |

### Security & Auth

| Feature | Status | Notes |
|---------|--------|-------|
| Device ingest token auth | ✅ Done | `X-Device-Token` header |
| Admin token auth | ✅ Done | `X-Admin-Token` header |
| Optional auth (disabled if secret not set) | ✅ Done | Fully backward compatible |
| CORS enabled | ✅ Done | All origins (for dev) |
| Multi-tenant isolation | ✅ Done | `tenant_id` field per bin |

### Database

| Feature | Status | Notes |
|---------|--------|-------|
| SQLite auto-create | ✅ Done | `smart_bins.db` created on first run |
| Sensor log history | ✅ Done | Timestamped per-reading storage |
| PostgreSQL migration | 📄 Documented | See `docs/DEPLOY_POSTGRES.md` |
| Bin upsert (INSERT OR REPLACE) | ✅ Done | Safe re-registration |

---

## 🤖 AI Engine Layer

| Feature | Status | Notes |
|---------|--------|-------|
| MobileNetV2 transfer learning | ✅ Done | `ai_engine/train_model.py` |
| Custom classifier head | ✅ Done | Dense + Dropout layers |
| 4-class waste classification | ✅ Done | Recyclable / Organic / Hazardous / General |
| Data augmentation | ✅ Done | Rotation, flip, zoom, brightness |
| Keras `.h5` model format | ✅ Done | Load from `ai_engine/models/` |
| Fallback when model missing | ✅ Done | Returns "Engine Offline" gracefully |
| Inference timing | ✅ Done | Returns inference duration in ms |
| Confidence thresholding | ✅ Done | Low confidence → "General" fallback |

---

## 🌐 Frontend Dashboard Layer (React)

### Navigation & Layout

| Feature | Status | Notes |
|---------|--------|-------|
| Collapsible sidebar | ✅ Done | 7 sections |
| Live sync indicator | ✅ Done | Pulses green, shows last sync time |
| System status dots (AI, IoT, Network) | ✅ Done | Sidebar bottom status bar |
| Dark/system theme | ✅ Done | CSS variables, no forced color mode |
| NEUROX branding | ✅ Done | Fully replaced all "Lovable" / "CleanCity" references |

### Overview Section

| Feature | Status |
|---------|--------|
| Total bins KPI card | ✅ Done |
| Priority bins KPI card | ✅ Done |
| Average fill level KPI | ✅ Done |
| Last sync time KPI | ✅ Done |
| Network snapshot bar chart | ✅ Done |
| Live event & operations log | ✅ Done |
| Priority bin dispatch queue | ✅ Done |
| IoT Event Simulator (3 triggers) | ✅ Done |

### City Map Section

| Feature | Status | Notes |
|---------|--------|-------|
| Leaflet interactive map | ✅ Done | OpenStreetMap tiles |
| Color-coded bin markers | ✅ Done | Green/Yellow/Orange/Red by fill % |
| Fill level tooltips | ✅ Done | Hover to see bin details |
| Optimized route polyline | ✅ Done | Blue dashed line |
| Depot marker | ✅ Done | Warehouse starting point |
| Route metrics (distance, time, CO2, fuel) | ✅ Done | Above map |
| Dispatch truck button | ✅ Done | Triggers modal simulation |

### Telemetry Section

| Feature | Status |
|---------|--------|
| Per-bin sensor cards | ✅ Done |
| Fill progress bar (color-coded) | ✅ Done |
| Temperature display | ✅ Done |
| Gas level display (ppm) | ✅ Done |
| Battery percentage | ✅ Done |
| Real/Simulated badge | ✅ Done |
| Sensor OK / error indicator | ✅ Done |

### Alerts Section

| Feature | Status | Notes |
|---------|--------|-------|
| Critical fill ≥80% card | ✅ Done | Red border |
| Fill warning 60–79% card | ✅ Done | Amber border |
| High temperature >40°C card | ✅ Done | Orange border |
| Gas hazard >150ppm card | ✅ Done | Purple border |
| Low battery <15% card | ✅ Done | Blue border |
| Summary banner (green/amber/red) | ✅ Done | Shows total alert count |
| Dispatch button from alerts | ✅ Done | Triggers collection modal |
| Live alert feed | ✅ Done | Timestamped list, severity pulse dots |
| Sidebar alert badge count | ✅ Done | Shows all 5 alert types |

### Toast Notifications (Real-time)

| Feature | Status | Notes |
|---------|--------|-------|
| Fill overflow toast | ✅ Done | Fires at ≥80%, deduped |
| Fill warning toast | ✅ Done | Fires at ≥60%, deduped |
| Gas hazard toast | ✅ Done | Fires at >150ppm, deduped |
| High temp toast | ✅ Done | Fires at >40°C, deduped |
| Low battery toast | ✅ Done | Fires at <15%, deduped |
| Auto-dismiss timers | ✅ Done | 6–10 seconds per type |
| Close button | ✅ Done | Manual dismiss |
| No-spam deduplication | ✅ Done | `useRef` tracks already-alerted bins |
| Auto-reset on condition clear | ✅ Done | Alert resets when value normalizes |

### Analytics Section

| Feature | Status |
|---------|--------|
| Fill level bar chart (all bins) | ✅ Done |
| Gas level bar chart | ✅ Done |
| Bin status summary cards | ✅ Done |
| Multi-metric line chart | ✅ Done |

### AI Vision Section

| Feature | Status |
|---------|--------|
| Image upload interface | ✅ Done |
| Classification result display | ✅ Done |
| Confidence percentage | ✅ Done |
| Disposal guidance text | ✅ Done |
| Offline mode message | ✅ Done |

### Community Section

| Feature | Status |
|---------|--------|
| Complaint submission form | ✅ Done |
| Citizen complaint feed | ✅ Done |

### Real-time Polling

| Feature | Status | Notes |
|---------|--------|-------|
| Telemetry auto-poll | ✅ Done | Every 6000ms (matches hardware 5s cycle) |
| Route data poll | ✅ Done | Every 6000ms |
| Manual refresh button | ✅ Done | Header refresh icon |
| Alert engine | ✅ Done | Runs on every bin state change |

---

## 📱 Responsive Design

| Breakpoint | Status |
|-----------|--------|
| Desktop (≥1024px) | ✅ Done |
| Tablet (768–1023px) | ✅ Done |
| Mobile (<768px) | ⚠️ Partial (dashboard is desktop-first) |

---

## 🔮 Future / Planned Features

| Feature | Priority | Notes |
|---------|----------|-------|
| PostgreSQL production database | High | See `docs/DEPLOY_POSTGRES.md` |
| WebSocket real-time push | Medium | Replace polling with WS events |
| Email / SMS alerts | Medium | For overflow and gas hazards |
| Historical trend graphs | Medium | 24h / 7d / 30d views |
| Multi-tenant admin panel | Low | Separate tenant management UI |
| Mobile app (React Native) | Low | For field workers |
| Predictive fill scheduling | Low | ML-based collection forecasting |
| ESP32-CAM integration | Planned | Live waste camera view |
