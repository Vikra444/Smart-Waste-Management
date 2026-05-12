import random
import sqlite3
import os
import time
import logging
from datetime import datetime
import sys

# Paths setup
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from alerts_engine.notifier import notifier
from backend_dashboard.config import *

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - IoT-SIM - %(levelname)s - %(message)s')
logger = logging.getLogger("IoT_Simulator")

class SmartBinSimulator:
    """
    Enterprise-Grade IoT Sensor Simulator for CleanCity AI.
    Simulates urban waste dynamics, sensor failures, and anomalies.
    """
    
    def __init__(self):
        self.locations = [
            ("Sector 1 (Market)", 23.2599, 77.4126, "MARKET"),
            ("BGI Campus", 23.2514, 77.4815, "RESIDENTIAL"),
            ("Main Market", 23.2352, 77.4244, "MARKET"),
            ("Railway Station", 23.2667, 77.4100, "MARKET"),
            ("Subhash Nagar", 23.2450, 77.4420, "RESIDENTIAL"),
            ("Arera Colony", 23.2167, 77.4167, "RESIDENTIAL"),
            ("MP Nagar (Comm)", 23.2333, 77.4333, "MARKET"),
            ("Habibganj", 23.2100, 77.4400, "MARKET"),
            ("Indrapuri", 23.2500, 77.4600, "RESIDENTIAL"),
            ("Govindpura (Ind)", 23.2600, 77.4500, "MARKET")
        ]

    def initialize_iot_grid(self):
        """Initializes tables for bins and telemetry logs"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            
            # Active Bins Table
            c.execute('''CREATE TABLE IF NOT EXISTS bins
                         (id INTEGER PRIMARY KEY, location TEXT, fill_level INTEGER, type TEXT, status TEXT, 
                          lat REAL, lon REAL, temp REAL, gas_level INTEGER, battery INTEGER, moisture INTEGER, 
                          zone TEXT, last_update TEXT)''')
            
            # Historical Logs Table
            c.execute('''CREATE TABLE IF NOT EXISTS sensor_logs
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, bin_id INTEGER, fill_level INTEGER, 
                          temp REAL, gas_level INTEGER, timestamp TEXT)''')
            
            c.execute("SELECT COUNT(*) FROM bins")
            if c.fetchone()[0] < 10:
                c.execute("DELETE FROM bins")
                initial_bins = []
                types = ['Recyclable', 'Organic', 'Non-Recyclable', 'Hazardous']
                for i, (loc, lat, lon, zone) in enumerate(self.locations):
                    initial_bins.append((
                        i+1, loc, random.randint(5, 40), random.choice(types), 'NORMAL', 
                        lat, lon, 28.0, 15, 100, 5, zone, datetime.now().isoformat()
                    ))
                c.executemany("INSERT INTO bins VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", initial_bins)
            
            conn.commit()
            conn.close()
            logger.info("IoT Grid and Logging Tables Initialized.")
        except Exception as e:
            logger.error(f"Initialization Failed: {e}")

    def update_telemetry(self):
        """Advanced telemetry update with zone intelligence and anomaly detection"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, fill_level, battery, temp, zone, location FROM bins")
            bins = c.fetchall()
            
            timestamp = datetime.now().isoformat()
            is_night = datetime.now().hour > 20 or datetime.now().hour < 6

            for b_id, fill, batt, temp, zone, loc in bins:
                # 1. Zone-Based Fill Rate
                rate_range = FILL_RATE_MARKET if zone == "MARKET" else FILL_RATE_RESIDENTIAL
                growth = random.randint(*rate_range)
                if is_night: growth = int(growth * 0.3) # Night slowdown
                
                new_fill = min(100, fill + growth)
                
                # 2. Battery Drain (More drain if sensors are active)
                new_batt = max(0, batt - random.uniform(0.1, 0.5))
                
                # 3. Environmental Logic
                new_temp = temp + random.uniform(-0.2, 0.5)
                new_gas = random.randint(10, 30) + (new_fill // 3)
                
                # 4. Anomaly Simulation (5% chance)
                status = 'NORMAL'
                if random.random() < 0.05:
                    event = random.choice(['FIRE', 'GAS_SPIKE', 'SENSOR_FAIL'])
                    if event == 'FIRE':
                        new_temp += 40
                        status = 'CRITICAL (FIRE)'
                        notifier.trigger_critical_alert(loc, "FIRE RISK DETECTED")
                    elif event == 'GAS_SPIKE':
                        new_gas += 60
                        status = 'HAZARDOUS GAS'
                        notifier.trigger_critical_alert(loc, "GAS SPIKE DETECTED")
                    elif event == 'SENSOR_FAIL':
                        status = 'OFFLINE'

                # 5. Threshold Validation
                if status == 'NORMAL':
                    if new_fill >= 90: status = 'CRITICAL'
                    elif new_fill >= 75: status = 'OVERFLOW SOON'
                    elif new_batt < BATTERY_CRITICAL: status = 'BATTERY LOW'

                # 6. Update Database
                c.execute("""UPDATE bins SET 
                             fill_level=?, battery=?, temp=?, gas_level=?, status=?, last_update=? 
                             WHERE id=?""", 
                          (new_fill, int(new_batt), round(new_temp, 1), new_gas, status, timestamp, b_id))
                
                # 7. Log Snapshot for Analytics
                c.execute("INSERT INTO sensor_logs (bin_id, fill_level, temp, gas_level, timestamp) VALUES (?,?,?,?,?)",
                          (b_id, new_fill, round(new_temp, 1), new_gas, timestamp))

            conn.commit()
            conn.close()
            logger.info(f"Grid Telemetry Updated at {timestamp}")
            return True
        except Exception as e:
            logger.error(f"Telemetry Sync Failure: {e}")
            return False

    def simulate_collection_reset(self, bin_ids):
        """Simulates physical collection resetting bin state"""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            for b_id in bin_ids:
                c.execute("UPDATE bins SET fill_level=0, status='NORMAL' WHERE id=?", (b_id,))
            conn.commit()
            conn.close()
            logger.info(f"Collection Event: Bins {bin_ids} have been emptied.")
        except Exception as e:
            logger.error(f"Collection Reset Failed: {e}")

iot_simulator = SmartBinSimulator()

if __name__ == "__main__":
    logger.info("--- CleanCity AI IoT Simulator Started ---")
    iot_simulator.initialize_iot_grid()
    
    try:
        while True:
            iot_simulator.update_telemetry()
            time.sleep(5) # Update every 5 seconds
    except KeyboardInterrupt:
        logger.info("Simulator Stopping...")
