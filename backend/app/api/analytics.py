from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.analytics import analytics_service
from app.services.route_analysis import route_analysis_service
from app.api import auth
from datetime import datetime, timedelta
import polyline

router = APIRouter()

@router.post("/aggregate-stats")
def aggregate_historical_stats(
    db: Session = Depends(get_db),
    # current_user: dict = Depends(auth.get_current_active_user) # In real app, restrict to Admin
):
    """
    Triggers the aggregation of historical incidents into stats.
    """
    try:
        count = analytics_service.calculate_historical_stats(db)
        return {"status": "success", "buckets_processed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/seed-test-data")
def seed_test_data(
    lat: float, lon: float,
    db: Session = Depends(get_db)
):
    """
    Seeds mock historical data for testing.
    """
    msg = analytics_service.test_seed_historical_data(db, lat, lon)
    return {"status": "success", "message": msg}

@router.get("/best-time")
async def get_best_time_to_leave(
    route_polyline: str,
    db: Session = Depends(get_db)
    # current_user: dict = Depends(auth.get_current_active_user)
):
    """
    Predicts safety score for the given route at: Now, +30m, +1h, +2h
    """
    now = datetime.now()
    times_to_check = [
        now,
        now + timedelta(minutes=30),
        now + timedelta(hours=1),
        now + timedelta(hours=2)
    ]
    
    predictions = []
    
    try:
        for t in times_to_check:
            # Note: predict_route_safety is async
            result = await route_analysis_service.predict_route_safety(route_polyline, t, db)
            predictions.append({
                "time_label": t.strftime("%I:%M %p"),
                "timestamp": t.isoformat(),
                "safety_score": result['safety_score'],
                "risk_level": result['risk_level'],
                "historical_incident_count": result['historical_incident_count']
            })
            
        # Recommend best
        best = max(predictions, key=lambda x: x['safety_score'])
        
        return {
            "predictions": predictions,
            "best_time": best
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
