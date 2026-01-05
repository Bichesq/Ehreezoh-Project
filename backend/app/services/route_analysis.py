from typing import List, Dict, Tuple, Any, Set
import math
import uuid
import polyline
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from shapely.geometry import LineString

from app.core.config import settings
from app.models.incident import Incident
from app.models.historical import HistoricalIncidentStats
from app.schemas.route import ScoredRoute, RouteIncident, RoutePreferences
from app.schemas.route import ScoredRoute, RouteIncident, RoutePreferences
import pygeohash
import httpx

class RouteAnalysisService:
    # ... (existing init)

    # ... (existing analyze_routes)

    # ... (existing _get_mock_routes)
    
    # ... (existing _find_incidents_on_route)
    
    # ... (existing _score_route_logic)

    async def predict_route_safety(self, route_polyline: str, target_time: datetime, db: Session) -> Dict[str, Any]:
        """
        Predicts safety score for a route at a future time based on historical data.
        """
        # 1. Decode polyline to get points
        points = polyline.decode(route_polyline) # List of (lat, lon)
        
        # 2. Get unique Geohashes (Precision 6) along the route
        # Sampling points every ~5th point to avoid over-processing (approx every 1km if points are sparse?)
        # Or just do all if efficient.
        unique_geohashes = set()
        for lat, lon in points:
             gh = pygeohash.encode(lat, lon, precision=6)
             unique_geohashes.add(gh)
        
        # 3. Query Historical Stats for these geohashes at target hour
        target_dow = target_time.weekday()
        target_hour = target_time.hour
        
        # Range query: target hour +/- 1 hour to smooth data
        hours_to_check = [target_hour] 
        # (Could expand to prev/next hour implies needing logic for day rollover, keeping simple for now)
        
        stats = db.query(HistoricalIncidentStats).filter(
            HistoricalIncidentStats.geohash.in_(unique_geohashes),
            HistoricalIncidentStats.day_of_week == target_dow,
            HistoricalIncidentStats.hour_of_day.in_(hours_to_check)
        ).all()
        
        # 4. Calculate Risk Score
        total_incidents = 0
        weighted_severity = 0.0
        
        for stat in stats:
            total_incidents += stat.incident_count
            weighted_severity += (stat.incident_count * stat.avg_severity)
            
        # Normalize
        # If 0 incidents, score is 100.
        # If many high severity incidents, score drops.
        
        # Mock formula:
        # Base risk = total_incidents * avg_severity
        # If route has 5 accidents historically at this hour -> High risk
        
        risk_metric = weighted_severity
        safety_score = max(0, 100 - (risk_metric * 2)) # Arbitrary scaling
        
        return {
            "safety_score": int(safety_score),
            "historical_incident_count": total_incidents,
            "risk_level": self._get_label_for_score(int(safety_score), 0)
        }

    # ... (existing methods)
    def __init__(self):
        self.mapbox_token = settings.MAPBOX_ACCESS_TOKEN

    async def analyze_routes(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        ride_type: str,
        preferences: RoutePreferences,
        db: Session,
        user_permissions: List[str] = []
    ) -> List[ScoredRoute]:
        
        if "Placeholder" in self.mapbox_token or len(self.mapbox_token) < 10:
             base_routes = self._get_mock_routes(origin, destination)
        else:
             base_routes = await self._fetch_routes_from_mapbox(origin, destination)
        
        scored_routes = []
        
        for idx, route_data in enumerate(base_routes):
            # 2. Find incidents on route
            incidents = self._find_incidents_on_route(db, route_data['geometry'], buffer_meters=200)
            
            # Filter incidents based on permissions (e.g., police)
            filtered_incidents = [
                i for i in incidents 
                if i.type != 'police' or 'view_police_checkpoints' in user_permissions
            ]
            
            # 3. Score Route
            score, route_incidents, warnings = self._score_route_logic(
                route_data, filtered_incidents, preferences
            )
            
            scored_routes.append(ScoredRoute(
                id=f"route_{idx}_{uuid.uuid4().hex[:8]}",
                geometry_encoded=route_data['polyline'],
                distance_km=route_data['distance_km'],
                duration_minutes=route_data['duration_minutes'],
                score=score,
                rank=0, # Will sort later
                label=self._get_label_for_score(score, idx),
                incidents=route_incidents,
                warnings=warnings,
                historical_notes=[] # TODO: Add later
            ))
            
        # 4. Rank routes
        scored_routes.sort(key=lambda x: x.score, reverse=True)
        for i, r in enumerate(scored_routes):
            r.rank = i + 1
            if i == 0 and r.score > 80:
                r.label = "Recommended"
            
        return scored_routes

    def _get_mock_routes(self, origin: Tuple[float, float], dest: Tuple[float, float]) -> List[Dict]:
        """
        Generates 3 simulated routes:
        1. Direct (Shortest)
        2. Slightly curved (Alternative 1)
        3. More curved (Alternative 2)
        """
        routes = []
        
        # Calculate rough distance
        dist_km = self._haversine(origin[1], origin[0], dest[1], dest[0])
        base_dur = int(dist_km * 3) # Approx 20km/h avg in traffic
        
        # Route A: Direct
        routes.append({
            'geometry': LineString([origin, dest]),
            'polyline': polyline.encode([origin[::-1], dest[::-1]]), # polyline expects (lat, lon)
            'distance_km': round(dist_km, 2),
            'duration_minutes': base_dur
        })
        
        # Route B: Slight Datour (via midpoint offset)
        mid = ((origin[0] + dest[0])/2, (origin[1] + dest[1])/2)
        offset_b = (mid[0] + 0.01, mid[1] + 0.01) # ~1km offset
        geom_b = LineString([origin, offset_b, dest])
        routes.append({
            'geometry': geom_b,
            'polyline': polyline.encode([origin[::-1], offset_b[::-1], dest[::-1]]),
            'distance_km': round(dist_km * 1.2, 2),
            'duration_minutes': int(base_dur * 1.2)
        })
        
        # Route C: Major Detour
        offset_c = (mid[0] - 0.015, mid[1] - 0.005)
        geom_c = LineString([origin, offset_c, dest])
        routes.append({
            'geometry': geom_c,
            'polyline': polyline.encode([origin[::-1], offset_c[::-1], dest[::-1]]),
            'distance_km': round(dist_km * 1.4, 2),
            'duration_minutes': int(base_dur * 1.4)
        })
        
        return routes

    async def _fetch_routes_from_mapbox(self, origin: Tuple[float, float], dest: Tuple[float, float]) -> List[Dict]:
        """
        Fetches real routes from Mapbox Directions API.
        Falls back to mock routes if request fails.
        """
        # Mapbox expects "lon,lat"
        coords = f"{origin[0]},{origin[1]};{dest[0]},{dest[1]}"
        url = f"https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{coords}"
        
        params = {
            "access_token": self.mapbox_token,
            "alternatives": "true",
            "geometries": "polyline",
            "overview": "full",
            "steps": "true",
            "annotations": "congestion,duration,distance"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=5.0)
                response.raise_for_status()
                data = response.json()
                
            routes = []
            for r in data.get("routes", []):
                poly_str = r.get("geometry")
                
                # Decode polyline (lat, lon) -> LineString (lon, lat)
                decoded = polyline.decode(poly_str)
                # polyline.decode gives list of (lat, lon)
                # LineString needs list of (x, y) = (lon, lat)
                path_coords = [(lon, lat) for lat, lon in decoded]
                
                routes.append({
                    'geometry': LineString(path_coords),
                    'polyline': poly_str,
                    'distance_km': round(r.get("distance", 0) / 1000.0, 2),
                    'duration_minutes': int(r.get("duration", 0) / 60.0),
                    'congestion': r.get("legs", [{}])[0].get("annotation", {}).get("congestion", [])
                })
                
            if not routes:
                return self._get_mock_routes(origin, dest)
                
            return routes
            
        except Exception as e:
            print(f"Mapbox API retrieval failed: {e}")
            return self._get_mock_routes(origin, dest)

    def _find_incidents_on_route(self, db: Session, route_geom: LineString, buffer_meters: int) -> List[Incident]:
        """
        Finds active incidents within X meters of the route
        """
        # In a real PostGIS setup, we'd use ST_DWithin on the LineString
        # For now, simplistic bbox or radius check if 'route_geom' is complex?
        # Actually we should try to use PostGIS functions if available.
        
        # Construct WKT for route
        route_wkt = route_geom.wkt
        
        # Query
        # Note: 0.002 degrees approx 200m at equator
        return db.query(Incident).filter(
            Incident.status == 'active',
            func.ST_DWithin(
                Incident.location,
                func.ST_GeomFromText(route_wkt, 4326),
                buffer_meters,
                True # Use sphere (meters)
            )
        ).all()

    def _score_route_logic(
        self, 
        route_data: Dict, 
        incidents: List[Incident], 
        preferences: RoutePreferences
    ) -> Tuple[int, List[RouteIncident], List[str]]:
        
        score = 100
        mapped_incidents = []
        warnings = []
        
        base_types = {
            'accident': 30,
            'traffic_jam': 15,
            'roadblock': 50,
            'police': 10,
            'road_hazard': 20
        }
        
        for inc in incidents:
            penalty = base_types.get(inc.type, 10)
            
            # Adjust by confirmations (0 to 1 scale, max out at 10 confirmations)
            conf_factor = min(inc.confirmations / 5.0, 1.0)
            penalty = penalty * (0.5 + 0.5 * conf_factor) # Minimum 50% penalty even if unconfirmed
            
            # Severity score adjustment (if set)
            if inc.severity_score:
                penalty *= (inc.severity_score / 50.0)
                
            score -= penalty
            
            # Add to mapped list
            mapped_incidents.append(RouteIncident(
                id=inc.id,
                type=inc.type,
                severity="high" if penalty > 20 else "moderate" if penalty > 10 else "low",
                confirmations=inc.confirmations,
                distance_from_start_km=0.0, # TODO: Calculate linear referencing
                estimated_delay_minutes=5, # Placeholder
                location=(inc.longitude, inc.latitude),
                description=inc.description
            ))
            
            warnings.append(f"{inc.type.replace('_', ' ').title()} reported on route")

        # Floor score
        return max(0, int(score)), mapped_incidents, warnings

    def _get_label_for_score(self, score: int, idx: int) -> str:
        if score > 80: return "Safest"
        if score > 60: return "Balanced"
        return "Risky" if score < 40 else "Standard"

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2) * math.sin(dLat/2) + \
            math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
            math.sin(dLon/2) * math.sin(dLon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

route_analysis_service = RouteAnalysisService()
