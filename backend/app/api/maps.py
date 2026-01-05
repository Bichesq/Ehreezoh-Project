from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
import requests
from pydantic import BaseModel
from app.core.config import settings
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/maps", tags=["Maps"])

class PlaceResult(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float

@router.get("/search", response_model=List[PlaceResult])
def search_places(
    query: str = Query(..., min_length=2),
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
):
    """
    Search for places using Mapbox Geocoding API.
    Proxies request to avoid exposing API key on client.
    """
    if not settings.MAPBOX_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="Map configuration missing")

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    
    params = {
        "access_token": settings.MAPBOX_ACCESS_TOKEN,
        "limit": 5,
        "types": "poi,address,place",
        "country": "in", # Restrict to India
        "bbox": "73.8,29.5,76.9,32.5" # Restrict to Punjab
    }

    # Bias results to user location
    if latitude and longitude:
        params["proximity"] = f"{longitude},{latitude}"

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Mapbox error: {e}")
        raise HTTPException(status_code=502, detail="External map service failed")

    results = []
    for feature in data.get("features", []):
        # Mapbox returns [lon, lat]
        center = feature.get("center", [0, 0])
        results.append(PlaceResult(
            id=feature.get("id"),
            name=feature.get("text"), # Main name (e.g. Mvan Market)
            description=feature.get("place_name"), # Full address
            latitude=center[1],
            longitude=center[0]
        ))
    
    return results
