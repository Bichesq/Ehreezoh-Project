from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.incident import Incident
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/incidents", tags=["Incidents"])

class IncidentCreate(BaseModel):
    type: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    media_url: Optional[str] = None

class IncidentResponse(BaseModel):
    id: str
    type: str
    description: Optional[str]
    latitude: float
    longitude: float
    created_at: datetime
    confirmations: int

    class Config:
        orm_mode = True

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def report_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import timedelta
    from app.services.gamification import gamification_service
    
    # Permission Check for Sensitive Types - use trust_score
    SENSITIVE_TYPES = ['police', 'checkpoint', 'military']
    if incident.type.lower() in SENSITIVE_TYPES:
        # Trust Score >= 50 required (hidden on frontend, but enforced here)
        REQUIRED_SCORE = 50 
        user_trust = current_user.trust_score or 0
        if user_trust < REQUIRED_SCORE:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Trust Score must be at least {REQUIRED_SCORE} to report {incident.type}."
            )

    new_incident = Incident(
        user_id=current_user.id,
        type=incident.type,
        description=incident.description,
        latitude=incident.latitude,
        longitude=incident.longitude,
        media_url=incident.media_url
    )
    db.add(new_incident)
    
    # Update user stats
    current_user.total_reports = (current_user.total_reports or 0) + 1
    
    # Streak calculation
    today = datetime.utcnow().date()
    if current_user.last_report_date:
        last_date = current_user.last_report_date.date()
        if last_date == today - timedelta(days=1):
            # Continuing streak
            current_user.current_streak = (current_user.current_streak or 0) + 1
        elif last_date != today:
            # Streak broken, reset
            current_user.current_streak = 1
        # Same day = no streak change
    else:
        current_user.current_streak = 1
    
    # Update longest streak
    if (current_user.current_streak or 0) > (current_user.longest_streak or 0):
        current_user.longest_streak = current_user.current_streak
    
    current_user.last_report_date = datetime.utcnow()
    
    # Award trust score for report (10 per report, capped at 500 until verification)
    current_user.trust_score = min(500, (current_user.trust_score or 0) + 10)
    
    db.commit()
    db.refresh(new_incident)
    
    # Award points and check for badges
    gamification_service.award_points(db, current_user.id, 5, reason="incident_report")
    gamification_service.check_badges(db, current_user.id)
    
    # Broadcast Alert
    try:
        import pygeohash as pgh
        from app.core.websocket import manager, create_event
        
        gh = pgh.encode(new_incident.latitude, new_incident.longitude, precision=6)
        
        alert_data = {
            "id": new_incident.id,
            "type": new_incident.type,
            "latitude": new_incident.latitude,
            "longitude": new_incident.longitude,
            "description": new_incident.description,
            "created_at": new_incident.created_at.isoformat()
        }
        
        # Run async broadcast
        await manager.broadcast_to_area(
            center_geohash=gh,
            message=create_event(event_type="incident_alert", data=alert_data),
            include_neighbors=True
        )

        # --- Push Notification (MVP: Send to all other users) ---
        from app.services.notifications import notification_service
        
        # Get all device tokens except current user
        # In production, query geospatial index or topic subscription
        tokens_query = db.query(User.device_token).filter(
            User.device_token.isnot(None),
            User.id != current_user.id
        ).all()
        
        device_tokens = [t[0] for t in tokens_query if t[0]]
        
        if device_tokens:
            await notification_service.send_push_notification(
                to=device_tokens,
                title=f"New {new_incident.type} reported!",
                body=f"Near you: {new_incident.description or 'Check map for details'}",
                data={"incident_id": new_incident.id}
            )
            
    except Exception as e:
        # Don't fail the request if WS/Push fails
        print(f"Failed to broadcast incident: {e}")
        pass
        
    return new_incident

@router.get("/", response_model=List[IncidentResponse])
async def get_nearby_incidents(
    latitude: float,
    longitude: float,
    radius_km: float = 5.0,
    db: Session = Depends(get_db)
):
    # Simple bounding box approximation or just all recent incidents for MVP
    # For MVP: Return all incidents created in last 24h (to keep map clean)
    # Refinement: Add geospatial query logic if needed later
    
    # Filter by time (last 24 hours) - omitted for simplicity in demo
    
    # Basic lat/long filtering (approximate)
    # 1 deg lat ~= 111 km
    deg_radius = radius_km / 111.0
    
    incidents = db.query(Incident).filter(
        Incident.latitude.between(latitude - deg_radius, latitude + deg_radius),
        Incident.longitude.between(longitude - deg_radius, longitude + deg_radius)
    ).all()
    
    return incidents


@router.get("/feed")
async def get_incident_feed(
    page: int = 1,
    limit: int = 20,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get incidents as a social feed with reporter info.
    Returns paginated list of incidents with reporter profile data.
    """
    from sqlalchemy import desc, func
    from app.models.gamification import Badge, UserBadge
    from app.models.community import IncidentVerification
    
    offset = (page - 1) * limit
    
    # Base query - recent incidents first
    query = db.query(Incident).filter(
        Incident.status == 'active'
    ).order_by(desc(Incident.created_at))
    
    # Optional geo-filtering
    if latitude and longitude:
        deg_radius = 10 / 111.0  # ~10km radius
        query = query.filter(
            Incident.latitude.between(latitude - deg_radius, latitude + deg_radius),
            Incident.longitude.between(longitude - deg_radius, longitude + deg_radius)
        )
    
    total = query.count()
    incidents = query.offset(offset).limit(limit).all()
    
    # Build feed items with reporter info
    feed_items = []
    for inc in incidents:
        # Get reporter
        reporter = db.query(User).filter(User.id == inc.user_id).first()
        
        # Get reporter's highest badge
        highest_badge = None
        if reporter:
            user_badges = db.query(UserBadge).filter(
                UserBadge.user_id == reporter.id
            ).all()
            if user_badges:
                badge_ids = [ub.badge_id for ub in user_badges]
                badges = db.query(Badge).filter(Badge.id.in_(badge_ids)).all()
                # Find badge with highest requirement_value
                if badges:
                    highest_badge = max(badges, key=lambda b: b.requirement_value or 0)
        
        # Get verification counts
        still_there_count = db.query(func.count(IncidentVerification.id)).filter(
            IncidentVerification.incident_id == inc.id,
            IncidentVerification.verification_type == 'still_there'
        ).scalar() or 0
        
        all_clear_count = db.query(func.count(IncidentVerification.id)).filter(
            IncidentVerification.incident_id == inc.id,
            IncidentVerification.verification_type == 'all_clear'
        ).scalar() or 0
        
        # Calculate trust level
        def get_trust_level(score):
            if score >= 500: return {"name": "Legend", "icon": "👑"}
            if score >= 300: return {"name": "Elder", "icon": "🦁"}
            if score >= 150: return {"name": "Guardian", "icon": "🛡️"}
            if score >= 50: return {"name": "Trusted", "icon": "✅"}
            return {"name": "Newcomer", "icon": "🌱"}
        
        reporter_trust = get_trust_level(reporter.trust_score or 0) if reporter else None
        
        feed_items.append({
            "id": inc.id,
            "type": inc.type,
            "description": inc.description,
            "latitude": inc.latitude,
            "longitude": inc.longitude,
            "media_url": inc.media_url,
            "created_at": inc.created_at.isoformat(),
            "status": inc.status,
            "is_verified": inc.is_verified,
            "confirmations": inc.confirmations or 0,
            "reporter": {
                "id": reporter.id if reporter else None,
                "name": reporter.full_name if reporter else "Anonymous",
                "profile_photo_url": reporter.profile_photo_url if reporter else None,
                "trust_score": reporter.trust_score if reporter else 0,
                "trust_level": reporter_trust,
                "badge": {
                    "name": highest_badge.name,
                    "icon": highest_badge.icon_url
                } if highest_badge else None
            },
            "verifications": {
                "still_there": still_there_count,
                "all_clear": all_clear_count
            },
            "impact": {
                "people_helped": (still_there_count * 3) + (inc.confirmations or 0)  # Estimate
            }
        })
    
    return {
        "items": feed_items,
        "page": page,
        "limit": limit,
        "total": total,
        "has_more": (page * limit) < total
    }

class VerificationRequest(BaseModel):
    verification_type: str  # 'still_there' or 'all_clear'

@router.post("/{incident_id}/verify")
async def verify_incident(
    incident_id: str,
    verification: VerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.community import IncidentVerification
    from app.services.gamification import gamification_service
    
    # 1. Check if incident exists
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    # 2. Check if user already verified
    existing_verification = db.query(IncidentVerification).filter(
        IncidentVerification.incident_id == incident_id,
        IncidentVerification.user_id == current_user.id
    ).first()
    
    if existing_verification:
        # Update existing verification
        existing_verification.verification_type = verification.verification_type
        # In a real app, we might check if they changed their mind and adjust counts accordingly
    else:
        # Create new verification
        new_verification = IncidentVerification(
            incident_id=incident_id,
            user_id=current_user.id,
            verification_type=verification.verification_type
        )
        db.add(new_verification)
        
        # Award points for first-time verification
        gamification_service.award_points(db, current_user.id, 2, "incident_verification")
        
    # 3. Update cached counts
    if verification.verification_type == 'still_there':
        incident.confirmations = (incident.confirmations or 0) + 1
    
    db.commit()
    
    # 4. Determine if incident should be cleared
    # Simple logic: If 'all_clear' votes > threshold or 'still_there', handle auto-resolve (future task)
    
    # 5. Broadcast update
    import pygeohash as pgh
    from app.core.websocket import manager, create_event
    
    gh = pgh.encode(incident.latitude, incident.longitude, precision=6)
    
    await manager.broadcast_to_area(
        center_geohash=gh,
        message=create_event(
            event_type="incident_verified", 
            data={
                "incident_id": incident_id,
                "verification_type": verification.verification_type,
                "confirmations": incident.confirmations
            }
        ),
        include_neighbors=True
    )

    return {"success": True, "message": "Verification recorded"}
