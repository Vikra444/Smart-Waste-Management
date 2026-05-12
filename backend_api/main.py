from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import os
import sys
import logging

# Paths setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ai_engine.classifier import classifier
from route_engine.optimizer import optimizer
from backend_dashboard.config import DB_PATH, CITY_CENTER
from backend_api.database.manager import db_manager
from backend_api.schemas.api_models import IoTUpdateRequest, AIResponse, BinTelemetry

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="CleanCity AI - IoT & Mobile Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "CleanCity AI Gateway Online", "version": "2.5.0-PRO"}

@app.get("/health")
def health_check():
    """System health check for monitoring"""
    db_status = "Connected" if db_manager.get_connection() else "Disconnected"
    return {
        "status": "Operational",
        "database": db_status,
        "ai_engine": "Ready",
        "iot_gateway": "Active"
    }

@app.get("/telemetry")
def get_telemetry():
    """Returns live bin data for the mobile map"""
    conn = db_manager.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Connection Failed")
    
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM bins")
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        logging.error(f"Telemetry Fetch Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict", response_model=AIResponse)
async def predict_waste(file: UploadFile = File(...)):
    """Real AI inference for mobile scanner"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        label, conf, guide, timing = classifier.predict(img)
        
        logging.info(f"AI Prediction: {label} ({conf*100:.1f}%)")
        return {
            "label": label,
            "confidence": conf,
            "guidance": guide,
            "inference_time": timing
        }
    except Exception as e:
        logging.error(f"Inference Error: {e}")
        raise HTTPException(status_code=500, detail="AI Engine Error")

@app.post("/iot/update")
def update_bin_telemetry(data: IoTUpdateRequest):
    """
    Endpoint for real ESP32 hardware to update bin status.
    Updates the bin mode to 'Real' and logs telemetry.
    """
    conn = db_manager.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Connection Failed")
    
    try:
        c = conn.cursor()
        # Update bin data and mark as 'Real' hardware
        c.execute("""
            UPDATE bins 
            SET fill_level = ?, gas_level = ?, temp = ?, battery = ?, status = 'Real'
            WHERE id = ?
        """, (data.fill_level, data.gas_level, data.temperature, data.battery, data.bin_id))
        
        if c.rowcount == 0:
            # If bin doesn't exist, create it (Simplified for demo)
            logging.warning(f"Hardware Update for unknown Bin ID: {data.bin_id}")
            # Optional: Auto-register logic here
            
        conn.commit()
        conn.close()
        
        logging.info(f"Hardware Sync: Bin {data.bin_id} | Fill: {data.fill_level}%")
        return {"status": "Hardware Data Synchronized", "bin_id": data.bin_id}
    except Exception as e:
        logging.error(f"IoT Update Error: {e}")
        raise HTTPException(status_code=500, detail="Telemetry Sync Failed")

@app.get("/route")
def get_optimized_route():
    """Returns optimized collection path for driver mode"""
    conn = db_manager.get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM bins")
        bins = [dict(row) for row in c.fetchall()]
        conn.close()
        
        route = optimizer.calculate_optimal_path(CITY_CENTER, bins)
        metrics = optimizer.get_eta_metrics(route)
        return {"route": route, "metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Routing Engine Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
