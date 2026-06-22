import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import csv
import io
import logging
import os
import sys

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ai_engine.classifier import classifier
from backend_api import settings
from backend_api.bin_validation import validate_bin_row, validate_bulk
from backend_api.database.manager import db_manager
from backend_api.deps_auth import require_admin_secret, require_device_ingest_token
from backend_api.schemas.api_models import AIResponse, BinBulkRequest, BinCreate, IoTUpdateRequest
from backend_api.settings import CITY_CENTER
from iot_gateway.sensor_simulator import iot_simulator
from route_engine.optimizer import optimizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    iot_simulator.initialize_iot_grid()
    
    async def simulation_loop():
        while True:
            await asyncio.sleep(5)
            try:
                await asyncio.to_thread(iot_simulator.jitter_simulated_data)
            except Exception as e:
                logging.error("Simulator error: %s", e)

    task = asyncio.create_task(simulation_loop())
    yield
    task.cancel()


app = FastAPI(title="CleanCity AI - IoT Gateway", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CleanCity AI | API Status</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0d1117;
            --card-bg: rgba(22, 27, 34, 0.8);
            --border-color: #30363d;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --accent-green: #2ea043;
            --accent-glow: rgba(46, 160, 67, 0.15);
        }
        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }
        .container {
            max-width: 600px;
            width: 90%;
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
            text-align: center;
            animation: fadeIn 0.8s ease-out;
            position: relative;
        }
        .container::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(135deg, var(--accent-green), transparent);
            border-radius: 18px;
            z-index: -1;
            opacity: 0.5;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .logo {
            font-size: 3rem;
            color: var(--accent-green);
            margin-bottom: 20px;
            display: inline-block;
            animation: pulse 2s infinite ease-in-out;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); filter: drop-shadow(0 0 2px var(--accent-green)); }
            50% { transform: scale(1.05); filter: drop-shadow(0 0 10px var(--accent-green)); }
        }
        h1 {
            font-size: 2.2rem;
            margin: 0 0 10px 0;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .badge {
            background-color: rgba(46, 160, 67, 0.15);
            color: var(--accent-green);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            border: 1px solid rgba(46, 160, 67, 0.3);
            display: inline-block;
            margin-bottom: 30px;
        }
        p {
            color: var(--text-secondary);
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        .links-group {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .btn {
            padding: 14px 28px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
        }
        .btn-primary {
            background-color: var(--accent-green);
            color: white;
            box-shadow: 0 4px 14px var(--accent-glow);
        }
        .btn-primary:hover {
            background-color: #2c973e;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(46, 160, 67, 0.3);
        }
        .btn-secondary {
            background-color: transparent;
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }
        .btn-secondary:hover {
            background-color: rgba(255, 255, 255, 0.05);
            border-color: #8b949e;
            transform: translateY(-2px);
        }
        .footer {
            margin-top: 40px;
            font-size: 0.85rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
        }
        .footer code {
            background: rgba(255, 255, 255, 0.05);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">♻️</div>
        <h1>CleanCity AI</h1>
        <div class="badge">Backend API Operational</div>
        <p>The FastAPI engine is running and ready. Access the documentation or redirect to the React frontend dashboard below.</p>
        <div class="links-group">
            <a href="http://localhost:3000" class="btn btn-primary">
                Open React Dashboard (Port 3000)
            </a>
            <a href="/docs" class="btn btn-secondary">
                Explore Interactive API Docs
            </a>
        </div>
        <div class="footer">
            FastAPI Node running at <code>http://localhost:8000</code>
        </div>
    </div>
</body>
</html>"""


@app.get("/health")
def health_check():
    db_status = "Connected" if db_manager.get_connection() else "Disconnected"
    return {
        "status": "Operational",
        "database": db_status,
        "ai_engine": "Ready" if classifier.active_backend == "keras" else "No model file",
        "ai_backend": classifier.active_backend,
        "iot_gateway": "Active",
        "device_auth_required": bool(settings.DEVICE_INGEST_SECRET),
        "admin_routes_enabled": bool(settings.ADMIN_API_SECRET),
    }


def _tenant_or_default(tid: str | None) -> str:
    t = (tid or "").strip()
    return t if t else settings.DEFAULT_TENANT_ID


@app.post("/bins")
def register_bin(
    body: BinCreate,
    _: None = Depends(require_device_ingest_token),
):
    ok, msg = validate_bin_row(body)
    if not ok:
        raise HTTPException(status_code=422, detail=msg)
    conn = db_manager.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Connection Failed")
    try:
        c = conn.cursor()
        ts = datetime.now().isoformat()
        c.execute(
            """INSERT OR REPLACE INTO bins
               (id, location, fill_level, type, status, lat, lon, temp, gas_level, battery, moisture, zone, tenant_id, last_update)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                body.id,
                body.location.strip(),
                body.fill_level,
                body.waste_type,
                body.status,
                body.lat,
                body.lon,
                body.temp,
                int(body.gas_level),
                body.battery,
                body.moisture,
                body.zone,
                body.tenant_id.strip(),
                ts,
            ),
        )
        conn.commit()
        conn.close()
        return {"status": "registered", "bin_id": body.id, "tenant_id": body.tenant_id.strip()}
    except Exception as e:
        logging.error("register_bin: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


def _register_bins_bulk_execute(bins: list[BinCreate]) -> dict:
    conn = db_manager.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Connection Failed")
    try:
        c = conn.cursor()
        ts = datetime.now().isoformat()
        for b in bins:
            okr, m = validate_bin_row(b)
            if not okr:
                conn.close()
                raise HTTPException(status_code=422, detail=m)
            c.execute(
                """INSERT OR REPLACE INTO bins
                   (id, location, fill_level, type, status, lat, lon, temp, gas_level, battery, moisture, zone, tenant_id, last_update)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    b.id,
                    b.location.strip(),
                    b.fill_level,
                    b.waste_type,
                    b.status,
                    b.lat,
                    b.lon,
                    b.temp,
                    int(b.gas_level),
                    b.battery,
                    b.moisture,
                    b.zone,
                    b.tenant_id.strip(),
                    ts,
                ),
            )
        conn.commit()
        conn.close()
        return {"status": "registered", "count": len(bins)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error("bulk: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/bins/bulk")
def register_bins_bulk(
    body: BinBulkRequest,
    _: None = Depends(require_device_ingest_token),
):
    ok, msg, _ = validate_bulk(body.bins)
    if not ok:
        raise HTTPException(status_code=422, detail=msg)
    return _register_bins_bulk_execute(body.bins)


@app.post("/bins/import-csv")
async def import_bins_csv(
    file: UploadFile = File(...),
    _: None = Depends(require_device_ingest_token),
):
    """CSV columns: id,location,lat,lon,zone,waste_type,fill_level,gas_level,temp,battery,moisture,status,tenant_id"""
    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8")
    reader = csv.DictReader(io.StringIO(text))
    required = {
        "id",
        "location",
        "lat",
        "lon",
    }
    if not reader.fieldnames or not required.issubset({h.strip() for h in reader.fieldnames}):
        raise HTTPException(
            status_code=400,
            detail=f"CSV header must include {sorted(required)} (got {reader.fieldnames})",
        )
    bins: list[BinCreate] = []
    errors: list[str] = []
    for i, row in enumerate(reader, start=2):
        try:
            fn = {k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k}
            b = BinCreate(
                id=int(fn["id"]),
                location=fn["location"],
                lat=float(fn["lat"]),
                lon=float(fn["lon"]),
                zone=fn.get("zone") or "UNKNOWN",
                waste_type=fn.get("waste_type") or "Mixed",
                fill_level=int(fn.get("fill_level") or 0),
                gas_level=float(fn.get("gas_level") or 0),
                temp=float(fn.get("temp") or 25),
                battery=int(fn.get("battery") or 100),
                moisture=int(fn.get("moisture") or 0),
                status=fn.get("status") or "NORMAL",
                tenant_id=fn.get("tenant_id") or settings.DEFAULT_TENANT_ID,
            )
            ok, msg = validate_bin_row(b)
            if not ok:
                errors.append(f"row {i}: {msg}")
                continue
            bins.append(b)
        except (ValueError, KeyError) as e:
            errors.append(f"row {i}: {e}")
    if errors and not bins:
        raise HTTPException(status_code=422, detail={"errors": errors[:50]})
    if not bins:
        raise HTTPException(status_code=400, detail="No valid rows")
    if errors:
        raise HTTPException(status_code=422, detail={"imported": len(bins), "errors": errors[:50]})
    ok, msg, _ = validate_bulk(bins)
    if not ok:
        raise HTTPException(status_code=422, detail=msg)
    return _register_bins_bulk_execute(bins)


@app.get("/telemetry")
def get_telemetry(tenant_id: str | None = Query(None, description="Filter bins by tenant")):
    conn = db_manager.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Connection Failed")
    try:
        c = conn.cursor()
        tid = (tenant_id or "").strip()
        if tid:
            c.execute("SELECT * FROM bins WHERE tenant_id = ?", (tid,))
        else:
            c.execute("SELECT * FROM bins")
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        logging.error("Telemetry Fetch Error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=AIResponse)
async def predict_waste(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        label, conf, guide, timing = classifier.predict(img)
        if label == "Engine Offline":
            raise HTTPException(
                status_code=503,
                detail="No trained model. Add ai_engine/models/waste_model.h5 and ensure TensorFlow loads.",
            )
        logging.info("AI Prediction: %s (%.1f%%)", label, conf * 100)
        return {
            "label": label,
            "confidence": conf,
            "guidance": guide,
            "inference_time": timing,
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error("Inference Error: %s", e)
        raise HTTPException(status_code=500, detail="AI Engine Error")


@app.post("/iot/update")
def update_bin_telemetry(
    data: IoTUpdateRequest,
    _: None = Depends(require_device_ingest_token),
):
    conn = db_manager.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Connection Failed")
    try:
        c = conn.cursor()
        ts = datetime.now().isoformat()
        tid_default = _tenant_or_default(data.tenant_id)
        tid_opt = (data.tenant_id.strip() if data.tenant_id else None)

        c.execute("SELECT fill_level FROM bins WHERE id=?", (data.bin_id,))
        prev = c.fetchone()
        prev_fill = prev[0] if prev else None

        c.execute(
            """
            UPDATE bins
            SET fill_level = ?, gas_level = ?, temp = ?, battery = ?, status = 'Real', last_update = ?,
                tenant_id = COALESCE(?, tenant_id)
            WHERE id = ?
            """,
            (data.fill_level, data.gas_level, data.temperature, data.battery, ts, tid_opt, data.bin_id),
        )
        anomaly = ""
        if prev_fill is not None and abs(int(data.fill_level) - int(prev_fill)) >= settings.ANOMALY_JUMP_THRESHOLD:
            anomaly = "SUDDEN_FILL_JUMP"

        if c.rowcount == 0:
            if data.location and data.latitude is not None and data.longitude is not None:
                zone = data.zone or "UNKNOWN"
                c.execute(
                    """INSERT INTO bins
                       (id, location, fill_level, type, status, lat, lon, temp, gas_level, battery, moisture, zone, tenant_id, last_update)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        data.bin_id,
                        data.location.strip(),
                        data.fill_level,
                        "Mixed",
                        "Real",
                        data.latitude,
                        data.longitude,
                        data.temperature,
                        int(data.gas_level),
                        int(data.battery),
                        int(data.humidity) if data.humidity is not None else 0,
                        zone,
                        tid_default,
                        ts,
                    ),
                )
            else:
                conn.close()
                raise HTTPException(
                    status_code=404,
                    detail="Unknown bin_id. Register with POST /bins or include location, latitude, longitude.",
                )

        conn.commit()
        iot_simulator.log_reading(
            data.bin_id,
            data.fill_level,
            data.temperature,
            int(data.gas_level),
            anomaly_flags=anomaly or None,
        )
        conn.close()
        logging.info("Hardware sync: bin %s fill %s%%", data.bin_id, data.fill_level)
        return {"status": "Hardware Data Synchronized", "bin_id": data.bin_id, "anomaly_flags": anomaly or None}
    except HTTPException:
        raise
    except Exception as e:
        logging.error("IoT Update Error: %s", e)
        raise HTTPException(status_code=500, detail="Telemetry Sync Failed")


@app.post("/admin/prune-sensor-logs")
def admin_prune_logs(
    days: int = Query(..., ge=7, le=3650),
    __: None = Depends(require_admin_secret),
):
    try:
        n = iot_simulator.prune_sensor_logs(days)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"deleted_rows": n, "retention_days": days}


@app.post("/admin/rollup-sensor-logs-hourly")
def admin_rollup_hourly(
    lookback_days: int = Query(14, ge=1, le=365),
    __: None = Depends(require_admin_secret),
):
    n = iot_simulator.rollup_sensor_logs_hourly(lookback_days)
    return {"driver_rowcount": n, "lookback_days": lookback_days}


@app.get("/route")
def get_optimized_route(tenant_id: str | None = Query(None)):
    conn = db_manager.get_connection()
    try:
        c = conn.cursor()
        tid = (tenant_id or "").strip()
        if tid:
            c.execute("SELECT * FROM bins WHERE tenant_id = ?", (tid,))
        else:
            c.execute("SELECT * FROM bins")
        bins = [dict(row) for row in c.fetchall()]
        conn.close()
        route = optimizer.calculate_optimal_path(CITY_CENTER, bins)
        metrics = optimizer.get_eta_metrics(route)
        return {"route": route, "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Routing Engine Error")


class ComplaintCreate(BaseModel):
    user_name: str
    location: str
    type: str


@app.post("/complaints")
def submit_complaint(body: ComplaintCreate):
    conn = db_manager.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Connection Failed")
    try:
        c = conn.cursor()
        ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        c.execute(
            "INSERT INTO complaints (user_name, location, type, status, timestamp) VALUES (?, ?, ?, ?, ?)",
            (body.user_name.strip(), body.location.strip(), body.type.strip(), "Pending", ts),
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Complaint logged successfully"}
    except Exception as e:
        logging.error("submit_complaint: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/complaints")
def get_complaints(limit: int = 5):
    conn = db_manager.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Connection Failed")
    try:
        c = conn.cursor()
        c.execute("SELECT id, user_name as Citizen, location as Location, type as Issue, status as Status, timestamp as Timestamp FROM complaints ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        logging.error("get_complaints: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


class BinResetRequest(BaseModel):
    bin_ids: list[int]


@app.post("/bins/reset")
def reset_bins(body: BinResetRequest):
    try:
        iot_simulator.clear_bins_after_collection(body.bin_ids)
        return {"status": "success", "message": f"{len(body.bin_ids)} bins emptied"}
    except Exception as e:
        logging.error("reset_bins: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
