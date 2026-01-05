from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.incident import Incident
from app.models.historical import HistoricalIncidentStats
from datetime import datetime
import pygeohash
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    
    def calculate_historical_stats(self, db: Session):
        """
        Aggregates all incidents to update historical stats.
        Grouping by: Geohash (precision 6), Day of Week, Hour of Day
        """
        logger.info("Starting historical stats aggregation...")

        # 1. Fetch all confirmed incidents
        # In a real system, we might limit this to "newly closed" incidents or run daily.
        incidents = db.query(Incident).all() # Simplification for prototype
        
        stats_map = {} # Key: (geohash, dow, hour) -> {count, total_severity}

        for inc in incidents:
            if not inc.latitude or not inc.longitude:
                continue
            
            # Calculate metrics
            gh = pygeohash.encode(inc.latitude, inc.longitude, precision=6)
            created_at = inc.created_at or datetime.now()
            dow = created_at.weekday()
            hour = created_at.hour
            
            key = (gh, dow, hour)
            
            if key not in stats_map:
                stats_map[key] = {'count': 0, 'severity_sum': 0}
            
            stats_map[key]['count'] += 1
            # Severity mapping (mock): accident=5, police=3, road_closure=4, heavy_traffic=2
            severity = 3 
            if inc.type == 'accident': severity = 5
            elif inc.type == 'road_closure': severity = 4
            elif inc.type == 'heavy_traffic': severity = 2
            
            stats_map[key]['severity_sum'] += severity

        # 2. Upsert into DB
        for (geohash, dow, hour), data in stats_map.items():
            avg_sev = data['severity_sum'] / data['count']
            
            # Check existing
            existing = db.query(HistoricalIncidentStats).filter(
                HistoricalIncidentStats.geohash == geohash,
                HistoricalIncidentStats.day_of_week == dow,
                HistoricalIncidentStats.hour_of_day == hour
            ).first()
            
            if existing:
                existing.incident_count = data['count']
                existing.avg_severity = avg_sev
            else:
                new_stat = HistoricalIncidentStats(
                    geohash=geohash,
                    day_of_week=dow,
                    hour_of_day=hour,
                    incident_count=data['count'],
                    avg_severity=avg_sev
                )
                db.add(new_stat)
        
        db.commit()
        logger.info(f"Aggregation complete. Processed {len(stats_map)} unique time/loc buckets.")
        return len(stats_map)

    def test_seed_historical_data(self, db: Session, center_lat: float, center_lon: float):
        """
        Seeds mock data for verification.
        Creates a 'danger zone' at the given location on Friday at 5 PM (17:00).
        """
        gh = pygeohash.encode(center_lat, center_lon, precision=6)
        
        # Friday (4), 17:00 -> High Risk
        high_risk = HistoricalIncidentStats(
            geohash=gh,
            day_of_week=4, # Friday
            hour_of_day=17,
            incident_count=15,
            avg_severity=4.5
        )
        
        # Friday (4), 14:00 -> Low Risk
        low_risk = HistoricalIncidentStats(
            geohash=gh,
            day_of_week=4,
            hour_of_day=14,
            incident_count=1,
            avg_severity=1.0
        )
        
        # Upsert logic simplified for seed
        for item in [high_risk, low_risk]:
             existing = db.query(HistoricalIncidentStats).filter(
                HistoricalIncidentStats.geohash == item.geohash,
                HistoricalIncidentStats.day_of_week == item.day_of_week,
                HistoricalIncidentStats.hour_of_day == item.hour_of_day
            ).first()
             if existing:
                 existing.incident_count = item.incident_count
                 existing.avg_severity = item.avg_severity
             else:
                 db.add(item)
        
        db.commit()
        return "Seeded High Risk (Fri 17:00) vs Low Risk (Fri 14:00)"

analytics_service = AnalyticsService()
