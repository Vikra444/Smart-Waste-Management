from pydantic import BaseModel
from typing import List, Optional

class BinTelemetry(BaseModel):
    id: int
    location: str
    lat: float
    lon: float
    fill_level: int
    gas_level: float
    temperature: float
    battery: float
    status: str

class AIResponse(BaseModel):
    label: str
    confidence: float
    guidance: str
    inference_time: int

class RouteMetrics(BaseModel):
    total_distance: str
    total_time: str
    bins_collected: int
    fuel_saved: str
    co2_saved: str

class RouteResponse(BaseModel):
    route: List[dict]
    metrics: RouteMetrics

class HealthStatus(BaseModel):
    api_status: str
    ai_engine: str
    database: str
    uptime: str
    version: str

class IoTUpdateRequest(BaseModel):
    bin_id: int
    fill_level: int
    gas_level: float
    temperature: float
    humidity: float
    battery: float
    mode: str = "Real" # Default to Real for hardware updates
