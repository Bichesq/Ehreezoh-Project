from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime

class RoutePreferences(BaseModel):
    prioritize: str = "balanced"  # "safety", "speed", "balanced"
    avoid_police: bool = False
    max_detour_minutes: int = 10
    show_police_checkpoints: bool = False

class RouteAnalysisRequest(BaseModel):
    origin: Tuple[float, float] = Field(..., description="(longitude, latitude)")
    destination: Tuple[float, float] = Field(..., description="(longitude, latitude)")
    ride_type: str = "moto"  # "moto", "economy_car", "comfort_car"
    departure_time: Optional[datetime] = None
    preferences: RoutePreferences = RoutePreferences()

class RouteIncident(BaseModel):
    id: str
    type: str
    severity: str  # "low", "moderate", "severe"
    confirmations: int
    distance_from_start_km: float
    estimated_delay_minutes: int
    location: Tuple[float, float]
    description: Optional[str] = None

class ScoredRoute(BaseModel):
    id: str
    geometry_encoded: str  # Polyline string
    distance_km: float
    duration_minutes: int
    score: int  # 0-100
    rank: int
    label: str
    incidents: List[RouteIncident]
    warnings: List[str]
    historical_notes: List[str]

class RouteAnalysisResponse(BaseModel):
    routes: List[ScoredRoute]
    recommendation: Optional[str] = None
